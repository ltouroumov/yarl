from yarl.util import Singleton


@Singleton
class ServiceLocator:
    def __init__(self):
        self.factories = dict()
        self.instances = dict()

    def add_factory(self, name, factory):
        if name in self.factories:
            raise KeyError("Redefining factory for %s" % name)

        self.factories[name] = factory

    def add_instance(self, name, instance):
        if name in self.instances:
            raise KeyError("Overwriting instance of %s" % name)

        self.instances[name] = instance

    def get(self, name):
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
        self.instances[name] = factory(self)


class Inject:
    def __init__(self, **services):
        self.services = services

    def __call__(self, decorated):
        return Injector(decorated, self.services)


class Injector:
    def __init__(self, decorated, services):
        self.decorated = decorated
        self.services = services

    def __call__(self, locator, *args, **kwargs):
        if locator is not ServiceLocator:
            raise TypeError("First argument must be an instance of ServiceLocator")

        kwargs.update({attr: locator.get(name) for attr, name in self.services.items()})
        return self.decorated(*args, **kwargs)

    def __instancecheck__(self, inst):
        return isinstance(inst, self.decorated)
