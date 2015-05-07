import itertools as it
import argparse
from sfml import sf
from yarl.map import World
from yarl.map.chunk import Chunk
from yarl.block import *
from yarl.view import TileMap
from yarl.save import SaveFile

args_parser = argparse.ArgumentParser()
args_parser.add_argument('--video-mode', dest='video_mode', default='640:480')
args_parser.add_argument('--world', dest='world', default='world')
args_parser.add_argument('--rebuild', dest='rebuild', default=None)
args = args_parser.parse_args()

print("Loading Blocks ...")
registry = BlockRegistry()
registry.add(VoidBlock)
registry.add(FloorBlock)
registry.add(WallBlock)

print("Loading World ...")

save_file = SaveFile(args.world)
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
    world.save()
    print("Done!")

# create the main window
width, height = map(int, args.video_mode.split(':'))
window = sf.RenderWindow(sf.VideoMode(width, height), "pySFML Window")

tile_map = TileMap(sf.Vector2(9, 9))
tile_map.update(level, sf.Vector2(0, 0))

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
    window.display()  # update the window