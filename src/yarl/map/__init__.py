import pickle
from yarl.map.chunk import ChunkLoader, ChunkTree
from yarl.util import dump_vec2, load_vec2, make_slug
from sfml import sf
import os
import os.path as path


class World:
    def __init__(self, wpath, name):
        """
        Creates an empty world
        """
        self.path = wpath
        self.name = name
        self.size = sf.Vector2(16, 16)
        self.floors = dict()

    def __repr__(self):
        return "World(%s, size: %i by %i)" % (self.name, self.size.x, self.size.y)

    def __getstate__(self):
        return {'name': self.name,
                'size': dump_vec2(self.size),
                'floors': self.floors}

    def __setstate__(self, state):
        self.name = state['name']
        self.size = load_vec2(state['size'])
        self.floors = state['floors']
        # Re-Set world references when loading
        for key, floor in self.floors.items():
            floor.world = self

    @staticmethod
    def load(base_path):
        """
        Loads a world from disk
        """
        data_path = path.join(base_path, 'world.dat')
        with open(data_path, 'rb') as f:
            world = pickle.load(f)
            world.path = base_path
            return world

    def save(self):
        """
        Save world metadata to disk (NOTE: Chunks are not saved)
        """
        data_path = path.join(self.path, 'world.dat')
        if not path.exists(self.path):
            os.makedirs(self.path)

        with open(data_path, 'wb+') as f:
            pickle.dump(self, f)

    def floor(self, name):
        """
        Get a dungeon floor
        """
        if name not in self.floors:
            self.floors[name] = Floor(name, self.size, self)
        return self.floors[name]


class Floor:
    def __init__(self, name, size, world):
        """
        Creates an unpopulated dungeon floor
        """
        self.name = name
        self.size = size
        self.world = world
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

    def path(self):
        return path.join(self.world.path, make_slug(self.name))

    def save(self):
        self.loader.save()

    def load(self):
        pass