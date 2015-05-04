import itertools as it
import argparse
from sfml import sf
from yarl.map import World
from yarl.map.chunk import Chunk
from yarl.tile import BlockTile
from yarl.view import TileMap


args_parser = argparse.ArgumentParser()
args_parser.add_argument('--video-mode', dest='video_mode', default='640:480')
args_parser.add_argument('--world', dest='world', default='world')
args_parser.add_argument('--rebuild', dest='rebuild', action='store_true', default=False)
args = args_parser.parse_args()

print("Loading World ...")
world = World.load(args.world)
floor = world.floor("Ground")

if args.rebuild:
    print("Building World ...")
    p2 = sf.Vector2(floor.size.x // 2, floor.size.y // 2) * Chunk.size
    p1 = -p2
    all_pos = (sf.Vector2(x, y)
               for (x, y)
               in it.product(range(p1.x, p2.x), range(p1.y, p2.y)))

    for pos in all_pos:
        floor.set_tile(pos, BlockTile())

    print("Done!")

# create the main window
width, height = map(int, args.video_mode.split(':'))
window = sf.RenderWindow(sf.VideoMode(width, height), "pySFML Window")

map = TileMap(sf.Vector2(9, 9))

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

    window.display()  # update the window