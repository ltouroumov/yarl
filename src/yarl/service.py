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
