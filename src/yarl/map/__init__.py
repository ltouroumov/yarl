from yarl.map.chunk import ChunkLoader, ChunkTree
from sfml import sf
import pickle
from os import makedirs
from os.path import join, exists

"""
map module
"""


class World:
    def __init__(self, path, name="Unloaded!"):
        self.path = path
        self.name = name
        self.size = sf.Vector2(16, 16)
        self.floors = dict()

    def __getstate__(self):
        return {'name': self.name,
                'size': self.size,
                'floors': self.floors}

    def __setstate__(self, state):
        self.name = state['name']
        self.floors = state['floors']

    @staticmethod
    def load(base_path):
        data_path = join(base_path, 'world.dat')
        with open(data_path, 'rb') as f:
            return pickle.load(f)

    def save(self):
        data_path = join(self.path, 'world.dat')
        if not exists(self.path):
            makedirs(self.path)

        with open(data_path, 'wb+') as f:
            pickle.dump(self, f)

    def floor(self, name):
        if name not in self.floors:
            self.floors[name] = Floor(name, self.size)
        return self.floors[name]


class Floor:
    def __init__(self, name, size=sf.Vector2(0, 0)):
        """
        Creates an unloaded dungeon floor
        """
        self.name = name
        self.size = size
        self.loader = None
        self.chunks = None

    def __getstate__(self):
        return {'name': self.name,
                'size': self.size}

    def __setstate__(self, state):
        self.name = state['name']
        self.size = state['size']

    def save(self):
        pass

    def load(self):
        pass


class TownFloor(Floor):
    """
    Floor with the town shops on it
    """
    def __init__(self):
        super().__init__("Town", sf.Vector2(8, 8))