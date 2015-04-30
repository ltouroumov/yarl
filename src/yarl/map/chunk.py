from sfml import sf
from yarl.util import cantor_pairing


class ChunkLoader:
    def __init__(self, floor):
        self.floor = floor
        self.pool = dict()

    def get(self, cpos):
        hsh = cantor_pairing(cpos)

        if hsh not in self.pool:
            self.pool[hsh] = self.load_chunk(cpos)

        return self.pool[hsh]

    def purge(self):
        pass

    def load_chunk(self, cpos):
        return Chunk(cpos)


class ChunkTree:
    def __init__(self, origin, size, loader, is_leaf=False):
        self.origin = origin
        self.size = size
        self.loader = loader
        self.is_leaf = is_leaf
        if is_leaf:
            self.chunks = [None] * (self.x * self.y)
        else:
            self.chunks = [None] * 4

    def get_tile(self, pos):
        cpos = pos / Chunk.size
        if self.is_leaf:
            container = self.get_chunk(cpos)
        else:
            container = self.get_cell(cpos)

        return container.get_tile(pos)

    def get_chunk(self, cpos):
        if self.is_leaf:
            rpos = cpos - self.origin
            idx = abs(rpos.x) + self.size.x * abs(rpos.y)
            if self.chunks[idx] is None:
                self.chunks[idx] = self.loader.get(cpos)

            return self.chunks[idx]
        else:
            return self.get_cell(cpos).get_chunk(cpos)

    def get_cell(self, cpos):
        dist = self.origin - cpos
        idx = (dist.x < 0) + (dist.y < 0) * 2
        if idx not in self.chunks:
            self.chunks[idx] = self.build_cell(dist)

        return self.chunks[idx]

    def build_cell(self, dist):
        cell_size = self.size / 2
        is_leaf = abs(cell_size.x) <= 2 or abs(cell_size.y) <= 2

        if is_leaf:
            cell_origin = sf.Vector2(self.origin.x + (-1 if dist.x < 0 else 0) * cell_size.x,
                                     self.origin.y + (-1 if dist.y < 0 else 0) * cell_size.y)
        else:
            cell_origin = sf.Vector2(self.origin.x + (-1 if dist.x < 0 else 1) * cell_size.x,
                                     self.origin.y + (-1 if dist.y < 0 else 1) * cell_size.y)

        return ChunkTree(cell_origin, cell_size, self.loader, is_leaf)


class Chunk:
    size = 16

    def __init__(self, pos):
        self.pos = pos
        self.tiles = []

    def __eq__(self, other):
        return self.pos == other.pos