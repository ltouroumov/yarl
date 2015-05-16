from sfml import sf
from yarl.block import BlockRegistry
from yarl.util import cantor_pairing
from yarl.tile import Tile
from yarl.schema import ChunkTable
import numpy as np


class ChunkLoader:
    def __init__(self, level_id, save_file):
        self.level = level_id
        self.save_file = save_file
        self.pool = dict()

    def get(self, cpos):
        hsh = cantor_pairing(cpos.x, cpos.y)

        if hsh not in self.pool:
            self.pool[hsh] = self.load_chunk(cpos)

        return self.pool[hsh]

    def save(self):
        for hsh, chunk in self.pool.items():
            self.save_file.upsert(ChunkTable, chunk)

    def purge(self):
        pass

    def load_chunk(self, cpos):
        chunk = self.save_file.select(ChunkTable,
                                      pos=cpos,
                                      level_id=self.level)

        if chunk is None:
            chunk = Chunk(level_id=self.level,
                          pos=cpos)
            self.save_file.upsert(ChunkTable, chunk)

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

        cell = ChunkTree(origin=cell_origin,
                         size=cell_size,
                         loader=self.loader,
                         is_leaf=is_leaf)
        return cell


class TileMatrix(np.ndarray):
    def __new__(cls, shape):
        return super(TileMatrix, cls).__new__(cls, shape=shape, dtype=Tile)

    def pack(self):
        registry = BlockRegistry.instance()
        shape = "%s:%s" % self.shape

        def pack_tile(tile):
            if tile is None:
                return "0:0"
            else:
                return "%s:%s" % (registry.get_block_id(tile.block), tile.meta)

        def pack_row(row):
            prow = map(pack_tile, row)
            return str.join(';', prow)

        items = str.join('\n', map(pack_row, self))

        return (shape + '\n' + items).encode("ascii")

    @staticmethod
    def unpack(packed):
        shape_str, *rows = packed.decode('ascii').split('\n')
        shape = list(map(int, shape_str.split(":")))
        matrix = TileMatrix(shape=shape)
        registry = BlockRegistry.instance()
        for row_idx, row_str in enumerate(rows):
            cols = row_str.split(';')
            for col_idx, col_str in enumerate(cols):
                block_id, meta = col_str.split(':')
                block = registry.from_id(block_id)
                matrix[row_idx, col_idx] = Tile(block=block,
                                                meta=meta)

        return matrix


class Chunk:
    rank = 4
    size = 2 ** rank

    def __init__(self, level_id, pos, tiles=None):
        self.id = None
        self.level_id = level_id
        self.pos = pos
        if tiles is None:
            self.tiles = TileMatrix(shape=(self.size, self.size))
        else:
            self.tiles = tiles

    def __repr__(self):
        return "Chunk{ pos=(%i, %i) }" % (self.pos.x, self.pos.y)

    def get_tile(self, pos):
        rpos = pos - (self.pos * Chunk.size)

        if self.tiles[rpos.x, rpos.y] is None:
            self.tiles[rpos.x, rpos.y] = Tile()

        return self.tiles[rpos.x, rpos.y]

    def set_tile(self, pos, tile):
        rpos = pos - (self.pos * Chunk.size)
        self.tiles[rpos.x, rpos.y] = tile