import argparse
from yarl.asset import PackageManifest

args_parser = argparse.ArgumentParser(description="Builds the asset bundle")
args_parser.add_argument('manifest',
                         help="Package manifest (see documentation)")
args_parser.add_argument('--name',
                         dest='name',
                         default='package.zip',
                         help="Target archive name")
args = args_parser.parse_args()

manifest = PackageManifest(args.manifest)
manifest.build_archive(args.name)
