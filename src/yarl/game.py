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

        from sfml import sf

        """
        print("Loading World ...")

        save_file = SaveFile(self.args.world, 0)
        save_file.open()

        if self.args.rebuild:
            save_file.clear(self.args.rebuild)

        save_file.load()

        world = save_file.world
        region = world.region("Hub Town")
        level = region.level("Ground")

        if self.args.rebuild is not None:
            registry = Container.instance().get('engine.block_registry')
            print("Building World ...")
            p2 = sf.Vector2(level.size.x // 2, level.size.y // 2) * Chunk.size
            p1 = -p2
            all_pos = (sf.Vector2(x, y)
                       for (x, y)
                       in itertools.product(range(p1.x, p2.x), range(p1.y, p2.y)))

            for pos in all_pos:
                block = registry.get('block.floor')
                if pos.x % 4 == 0:
                    block = registry.get('block.wall')
                elif pos.y % 4 == 0:
                    block = registry.get('block.wall')

                level.set_block(pos, block)

            print("Saving ...")
            save_file.save()
            print("Done!")
        """
        try:
            # create the main window
            width, height = map(int, self.args.video_mode.split(':'))
            window = sf.RenderWindow(sf.VideoMode(width, height), "pySFML Window")
            # window.setVerticalSyncEnabled(True)
            # window.setFramerateLimit(30)

            # tile_map = TileMap(size=sf.Vector2(9, 9),
            #                    atlas=tile_atlas)
            # map_center = sf.Vector2(0, 0)
            # tile_map.update(level, map_center)
            # tile_map.transform.scale(sf.Vector2(2, 2))

            # start the game loop
            while window.is_open:
                # process events
                for event in window.events:
                    # close window: exit
                    if type(event) is sf.CloseEvent:
                        window.close()

                    message_bus.emit('sf.'+type(event).__name__, event, source='engine.main_window')

                window.clear()  # clear screen

                # scene_graph.update()
                # scene_graph.display(window)

                window.display()  # update the window
        except:
            from traceback import print_exc

            print("=== Exception Occured ===")
            print_exc()
