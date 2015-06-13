import argparse
import logging
import sys
from yarl.game import Game

if __name__ != "__main__":
    raise RuntimeError("Cannot import this module!")


args_parser = argparse.ArgumentParser()
args_parser.add_argument('--video-mode', dest='video_mode', default='640:480')
args_parser.add_argument('--world', dest='world', default='world')
args_parser.add_argument('--rebuild', dest='rebuild', default=None)
args_parser.add_argument('--load', dest='paks', nargs='*', default=[])
args_parser.add_argument('--no-core', dest='load_core', action='store_false', default=True)
args = args_parser.parse_args()

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s %(levelname)s in %(name)s] %(message)s',
                    datefmt='%I:%M:%S',
                    stream=sys.stdout)

Game(args).run()
