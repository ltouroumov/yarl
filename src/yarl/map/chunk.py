from sfml import sf
from yarl.util import cantor_pairing, dump_vec2, load_vec2
from yarl.tile import Tile
import os.path as op
import os
import pickle as pi
import numpy as np


class ChunkLoader:
    def __init__(self, floor):
        self.floor = floor
        self.pool = dict()

    def get(self, cpos):
        hsh = cantor_pairing(cpos.x, cpos.y)

        if hsh not in self.pool:
            self.pool[hsh] = self.load_chunk(cpos)

        return self.pool[hsh]

    def save(self):
        floor_path = self.floor.path()
        if not op.exists(floor_path):
            os.makedirs(floor_path)
        for hsh, chunk in self.pool.items():
            chunk_path = self.chunk_path(hsh=hsh)
            chunk.write_to(chunk_path)

    def purge(self):
        pass

    def chunk_path(self, hsh=None, cpos=None):
        if hsh is None:
            hsh = cantor_pairing(cpos.x, cpos.y)

        return op.join(self.floor.path(), "%04x.dat" % hsh)

    def load_chunk(self, cpos):
        path = self.chunk_path(cpos=cpos)
        if op.exists(path):
            chunk = Chunk.read_from(path)
        else:
            chunk = Chunk(cpos)
        return chunk


class ChunkTree:
    def __init__(self, origin, size, loader, is_leaf=False):
        self.origin = origin
        self.size = size
        self.loader = loader
        self.is_leaf = is_leaf
        if is_leaf:
            self.chunks = np.ndarray(shape=(size.x, size.y), dtype=Chunk)
        else:
            self.chunks = np.ndarray(shape=(2, 2), dtype=ChunkTree)

    def __repr__(self):
        return "ChunkTree{ origin=(%i, %i), size=(%i, %i), is_leaf=%i }" % (self.origin.x, self.origin.y,
                                                                            self.size.x, self.size.y,
                                                                            self.is_leaf)

    def get_tile(self, pos):
        cpos = sf.Vector2(pos.x >> Chunk.rank,
                          pos.y >> Chunk.rank)

        if self.is_leaf:
            container = self.get_chunk(cpos)
        else:
            container = self.get_cell(cpos)

        return container.get_tile(pos)

    def set_tile(self, pos, tile):
        cpos = sf.Vector2(pos.x >> Chunk.rank,
                          pos.y >> Chunk.rank)

        if self.is_leaf:
            container = self.get_chunk(cpos)
        else:
            container = self.get_cell(cpos)

        container.set_tile(pos, tile)

    def get_chunk(self, cpos):
        if self.is_leaf:
            key = (cpos.x - self.origin.x, cpos.y - self.origin.y)
            if key not in self.chunks:
                self.chunks[key] = self.loader.get(cpos)

            return self.chunks[key]
        else:
            return self.get_cell(cpos).get_chunk(cpos)

    def get_cell(self, cpos):
        dist = cpos - self.origin
        key = (0 if dist.x < 0 else 1, 0 if dist.y < 0 else 1)
        if self.chunks[key] is None:
            self.chunks[key] = self.build_cell(dist)

        return self.chunks[key]

    def build_cell(self, dist):
        cell_size = self.size / 2

        is_leaf = cell_size.x <= 2 or cell_size.y <= 2

        if is_leaf:
            cell_origin = sf.Vector2(self.origin.x + (-1 if dist.x < 0 else 0) * cell_size.x,
                                     self.origin.y + (-1 if dist.y < 0 else 0) * cell_size.y)
        else:
            cell_origin = sf.Vector2(self.origin.x + (-1 if dist.x < 0 else 1) * cell_size.x // 2,
                                     self.origin.y + (-1 if dist.y < 0 else 1) * cell_size.y // 2)

        cell = ChunkTree(cell_origin, cell_size, self.loader, is_leaf)
        return cell


class Chunk:
    rank = 4
    size = 2**rank

    def __init__(self, pos):
        self.pos = pos
        self.tiles = np.ndarray(shape=(self.size, self.size), dtype=Tile)

    def __getstate__(self):
        return {'pos': dump_vec2(self.pos),
                'tiles': self.tiles}

    def __setstate__(self, state):
        self.pos = load_vec2(state['pos'])
        self.tiles = state['tiles']

    def __repr__(self):
        return "Chunk{ pos=(%i, %i) }" % (self.pos.x, self.pos.y)

    def write_to(self, path):
        with open(path, 'wb+') as f:
            pi.dump(self, f)

    @staticmethod
    def read_from(path):
        with open(path, 'rb') as f:
            return pi.load(f)

    def get_tile(self, pos):
        rpos = pos - (self.pos * Chunk.size)

        if self.tiles[rpos.x, rpos.y] is None:
            self.tiles[rpos.x, rpos.y] = Tile()

        return self.tiles[rpos.x, rpos.y]

    def set_tile(self, pos, tile):
        rpos = pos - (self.pos * Chunk.size)
        self.tiles[rpos.x, rpos.y] = tile