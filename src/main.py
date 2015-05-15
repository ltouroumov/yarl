import itertools as it
import argparse
from sfml import sf
from yarl.map.chunk import Chunk
from yarl.block import *
from yarl.view import TileMap, TileAtlas
from yarl.save import SaveFile
from yarl.asset import AssetProvider, TexturePool

args_parser = argparse.ArgumentParser()
args_parser.add_argument('--video-mode', dest='video_mode', default='640:480')
args_parser.add_argument('--world', dest='world', default='world')
args_parser.add_argument('--rebuild', dest='rebuild', default=None)
args = args_parser.parse_args()

print("Loading Blocks ...")
registry = BlockRegistry.instance()
registry.add(VoidBlock)
registry.add(FloorBlock)
registry.add(WallBlock)

print("Loading Assets ...")
asset_provider = AssetProvider(['assets.tar.gz'])
asset_provider.load()
tex_pool = TexturePool(asset_provider)

print("Loading Textures ...")
tile_atlas = TileAtlas(tex_pool=tex_pool,
                       size=sf.Vector2(16, 16),
                       order=16)
tile_atlas.build(registry)

print("Loading World ...")

save_file = SaveFile(args.world, 0)
save_file.open()

if args.rebuild:
    save_file.clear(args.rebuild)

save_file.load()

world = save_file.world
region = world.region("Hub Town")
level = region.level("Ground")

if args.rebuild is not None:
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

# create the main window
width, height = map(int, args.video_mode.split(':'))
window = sf.RenderWindow(sf.VideoMode(width, height), "pySFML Window")

tile_map = TileMap(size=sf.Vector2(9, 9),
                   atlas=tile_atlas)
try:
    tile_map.update(level, sf.Vector2(0, 0))
except Exception as e:
    from traceback import print_tb
    print_tb(e.__traceback__)

# start the game loop
while window.is_open:
    # process events
    for event in window.events:
        # close window: exit
        if type(event) is sf.CloseEvent:
            window.close()

        if type(event) is sf.KeyEvent and event.code == sf.Keyboard.Q:
            window.close()

    window.clear()  # clear screen
    window.draw(tile_map)

    # Display tile map
    # spr = sf.Sprite(tile_atlas.texture)
    # window.draw(spr)
    window.display()  # update the window