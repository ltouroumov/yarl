import argparse
import logging
import sys
from yarl.package import PackageManifest

args_parser = argparse.ArgumentParser(description="Builds the asset bundle")
args_parser.add_argument('manifest',
                         help="Package manifest (see documentation)")
args_parser.add_argument('--name',
                         dest='name',
                         default='package.zip',
                         help="Target archive name")
args = args_parser.parse_args()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%I:%M:%S',
                    stream=sys.stdout)

manifest = PackageManifest(args.manifest)
manifest.build_archive(args.name)
