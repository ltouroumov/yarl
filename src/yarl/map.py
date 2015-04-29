from yarl.map.chunk import ChunkLoader, ChunkTree


class World:
    def __init__(self, path, name="Unloaded!"):
        self.path = path
        self.name = name
        self.floors = dict()

    def floor(self, name):
        if name not in self.floors:
            self.floors[name] = Floor(name)
        return self.floors[name]


class Floor:
    def __init__(self, name):
        self.name = name
        self.chunks = ChunkTree(self)
        self.loader = ChunkLoader(self)

    def save(self):
        pass

    def load(self):
        pass