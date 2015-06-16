import itertools as it
import cProfile
import pstats
import io
from sfml import sf
from yarl.map.chunk import Chunk
from yarl.block import *
from yarl.view import TileMap, TileAtlas
from yarl.save import SaveFile

world_name = "profiler"

profiler = cProfile.Profile()

print("Loading Blocks ...")
registry = BlockRegistry.instance()
registry.add(VoidBlock)
registry.add(FloorBlock)
registry.add(WallBlock)

print("Loading Textures ...")
tile_atlas = TileAtlas(size=sf.Vector2(16, 16),
                       order=16)
tile_atlas.build(registry)

print("Loading World ...")

save_file = SaveFile(world_name, 0)
save_file.open()
save_file.clear(world_name)

save_file.load()

world = save_file.world
region = world.region("Hub Town")
level = region.level("Ground")

print("Building World ...")
p2 = sf.Vector2(level.size.x // 2, level.size.y // 2) * Chunk.size
p1 = -p2
all_pos = (sf.Vector2(x, y)
           for (x, y)
           in it.product(range(p1.x, p2.x), range(p1.y, p2.y)))

for pos in all_pos:
    level.set_block(pos, registry.get("block.floor"))

print("Saving ...")
save_file.save()
print("Done!")

tile_map = TileMap(size=sf.Vector2(9, 9),
                   atlas=tile_atlas)
tile_map.update(level, sf.Vector2(0, 0))

profiler.disable()

s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
