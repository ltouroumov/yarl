from yarl.asset import AssetLoader
from yarl.block import BlockRegistry
from yarl.debug import DebugConsole
from yarl.package import PackageLoader
from yarl.service import Container, Service


class GameBootstrap(object):
    package_loader = Service('engine.package_loader')

    def __init__(self):
        pass

    def load(self):
        for package in self.package_loader.packages:
            print(package)

        self.pre_init()
        self.init()
        self.post_init()

    def pre_init(self):
        pass

    def init(self):
        pass

    def post_init(self):
        pass


class Game(object):
    def __init__(self, args):
        self.args = args

    def load(self):
        print("Setting up services ...")
        container = Container.instance()

        print("Loader Setup")
        package_loader = PackageLoader(['core.zip'] + self.args.paks)
        package_loader.load()
        package_loader.hook()

        container.add_instance('engine.package_loader', package_loader)
        container.add_factory('engine.asset_loader', AssetLoader)
        container.add_factory('engine.block_registry', BlockRegistry)

    def boot(self):
        GameBootstrap().load()

    def run(self):
        self.load()
        self.boot()
