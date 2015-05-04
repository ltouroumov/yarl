import itertools as it
import cProfile
import pstats
import io

from sfml import sf
from yarl.map import World
from yarl.map.chunk import Chunk, ChunkTree
from yarl.tile import BlockTile


profiler = cProfile.Profile()

world = World.load("myworld")
floor = world.floor("Ground")

p2 = sf.Vector2(floor.size.x // 2, floor.size.y // 2) * Chunk.size
p1 = -p2
all_pos = (sf.Vector2(x, y)
           for (x, y)
           in it.product(range(p1.x, p2.x), range(p1.y, p2.y)))

profiler.enable()

for pos in all_pos:
    floor.set_tile(pos, BlockTile())

profiler.disable()

s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())