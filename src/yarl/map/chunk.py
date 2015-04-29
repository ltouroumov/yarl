__author__ = 'jdavid'


class ChunkLoader:
    def __init__(self, floor):
        self.floor = floor


class ChunkTree:
    def __init__(self, origin, size, loader, is_leaf):
        self.origin = origin
        self.size = size
        self.loader = loader
        self.is_leaf = is_leaf
        self.cells = []
        self.chunks = []

    def get_tile(self, pos):
        if self.is_leaf:
            container = self.get_chunk(pos)
        else:
            container = self.get_cell(pos)

        return container.get_tile(pos)

    def get_chunk(self, pos):
        return Chunk(self.origin + pos)

    def get_cell(self, pos):
        return ChunkTree(self.origin + pos, self.size, self.loader, self.is_leaf)


class Chunk:
    def __init__(self, pos):
        self.pos = pos
        self.tiles = []