from yarl.util import Singleton


@Singleton
class Container(object):
    def __init__(self):
        self.factories = dict()
        self.instances = dict()

        # Cyclic references >_<
        self.add_instance('service_container', self)

    def add_factory(self, name, factory):
        if name in self.factories:
            raise KeyError("Redefining factory for %s" % name)

        self.factories[name] = factory

    def add_instance(self, name, instance):
        if name in self.instances:
            raise KeyError("Overwriting instance of %s" % name)

        self.instances[name] = instance

    def service(self, name):
        if name not in self.instances:
            try:
                self.load(name)
            except KeyError:
                raise KeyError("Unable to find instance or load service %s" % name)

        return self.instances[name]

    def load(self, name):
        if name not in self.factories:
            raise KeyError("ServiceLocator does not have a factory for %s" % name)

        factory = self.factories[name]
        self.instances[name] = factory()


class Service(object):
    @staticmethod
    def get(name):
        return Container.get().service(name)

    def __init__(self, name):
        self.name = name
        self.cache = None

    def __get__(self, instance, owner):
        if self.cache is None:
            container = Container.get()
            self.cache = container.service(self.name)

        return self.cache

    def __set__(self, instance, value):
        raise RuntimeError("Cannot set an injected service property")

    def __delete__(self, instance):
        raise RuntimeError("Cannot delete an injected service property")


class Inject(object):
    def __init__(self, **services):
        self.services = services

    def __call__(self, decorated):
        return Injector(decorated, self.services)


class Injector(object):
    def __init__(self, decorated, services):
        self.decorated = decorated
        self.services = services

    def __call__(self, *args, **kwargs):
        locator = Container.get()
        kwargs.update({attr: locator.service(name) for attr, name in self.services.items()})
        return self.decorated(*args, **kwargs)

    def __instancecheck__(self, inst):
        return isinstance(inst, self.decorated)
