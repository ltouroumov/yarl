from yarl.map.chunk import ChunkLoader, ChunkTree
from yarl.util import dump_vec2, load_vec2
from sfml import sf


class World:
    def __init__(self, name, save):
        """
        Creates an empty world
        """
        self.save = save
        self.name = name
        self.size = sf.Vector2(16, 16)
        self.regions = dict()

    def __repr__(self):
        return "World(%s, size: %i by %i)" % (self.name, self.size.x, self.size.y)

    def region(self, name):
        """
        Get a dungeon floor
        """
        if name not in self.regions:
            self.regions[name] = Region(self.save, name, self.size)

        return self.regions[name]


class Region:
    """
    Create an unpopulated region
    """
    def __init__(self, save, name, size):
        self.id = None
        self.name = name
        self.save = save
        self.size = size
        self.levels = dict()

    def __repr__(self):
        return "Region(%s, %s levels)" % (self.name, len(self.levels))

    def level(self, name):
        if name not in self.levels:
            self.levels[name] = Level(name, self.size, self.save)


class Level:
    def __init__(self, name, size, save):
        """
        Creates an unpopulated dungeon floor
        """
        self.id = None
        self.name = name
        self.size = size
        self.save = save
        self.loaded = False
        self.loader = None
        self.chunks = None

    def __repr__(self):
        return "Floor(%s, size: %i by %i)" % (self.name, self.size.x, self.size.y)

    def __getstate__(self):
        return {'name': self.name,
                'size': dump_vec2(self.size)}

    def __setstate__(self, state):
        self.name = state['name']
        self.size = load_vec2(state['size'])
        self.loaded = False
        self.init()

    def init(self):
        if not self.loaded:
            self.loader = ChunkLoader(self)
            self.chunks = ChunkTree(sf.Vector2(0, 0), self.size, self.loader)
            self.loaded = True

    def get_tile(self, pos):
        self.init()
        return self.chunks.get_tile(pos)

    def set_tile(self, pos, tile):
        self.init()
        self.chunks.set_tile(pos, tile)

    def set_block(self, pos, block):
        self.init()
        self.chunks.get_tile(pos).set_block(block)

    def save(self):
        self.loader.save()

    def load(self):
        pass