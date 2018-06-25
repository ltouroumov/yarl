from yarl.asset import AssetLoader
from yarl.block import BlockRegistry
from yarl.message import MessageBus
from yarl.package import PackageLoader
from yarl.scene import SceneGraph
from yarl.util import apply_seq
from yarl.service import Container, Service
import importlib
import logging
import sys

logger = logging.getLogger(__name__)


class GameBootstrap(object):
    package_loader = Service('engine.package_loader')

    def __init__(self):
        self.loaders = list()

    def load(self):
        for name, package in self.package_loader.packages.items():
            for _, (loaders, meta) in package.index.loaders.items():
                base_package = meta['base_package']
                for loader in loaders:
                    module_name, class_name = (base_package + '.' + loader).rsplit('.', 1)
                    logger.debug("Importing %s", module_name)
                    module = importlib.import_module(module_name)
                    loader_class = getattr(module, class_name)
                    loader_instance = loader_class()
                    self.loaders.append(loader_instance)

        logger.info("pre_init phase")
        apply_seq(self.loaders, 'pre_init')
        logger.info("init phase")
        apply_seq(self.loaders, 'init')
        logger.info("post_init phase")
        apply_seq(self.loaders, 'post_init')


class ThreadRunner(object):
    def __init__(self):
        self.threads = list()

    def register(self, thread):
        self.threads.append(thread)

    def start(self):
        apply_seq(self.threads, 'start')


class Game(object):
    def __init__(self, args):
        self.args = args

    def load(self):
        formatter = logging.Formatter(fmt='[%(asctime)s %(levelname)s in %(name)s] %(message)s',
                                      datefmt='%I:%M:%S')

        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)

        logger.info("Setting up services")
        container = Container.instance
        container.add_instance('engine.default_formatter', formatter)

        logger.info("Package Loader")
        if self.args.load_core:
            self.args.packs.insert(0, 'core.zip')

        package_loader = PackageLoader(self.args.paks)
        package_loader.load()
        package_loader.hook()

        container.add_instance('engine.package_loader', package_loader)
        container.add_factory('engine.asset_loader', AssetLoader)
        container.add_factory('engine.block_registry', BlockRegistry)
        container.add_factory('engine.thread_runner', ThreadRunner)
        container.add_factory('engine.scene_graph', SceneGraph)
        container.add_factory('engine.message_bus', MessageBus)

    def boot(self):
        GameBootstrap().load()

    def run(self):
        self.load()
        self.boot()

        thread_runner = Service.get('engine.thread_runner')
        thread_runner.start()

        # scene_graph = Service.get('engine.scene_graph')
        message_bus = Service.get('engine.message_bus')

        try:
            from bearlibterminal import terminal

            terminal.open()
            terminal.printf(2, 2, "Test!")
            terminal.refresh()

            event = terminal.read()
            while event != terminal.TK_CLOSE:
                message_bus.emit('term.event', event, source='engine.main_window')
                terminal.refresh()
                event = terminal.read()

            terminal.close()
        except:
            from traceback import print_exc

            print("=== Exception Occured ===")
            print_exc()
