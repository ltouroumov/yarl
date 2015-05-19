import tarfile
import argparse
import json
from os.path import realpath, dirname, join


def compose(*funcs):
    """
    Composes two or more functions

    :param funcs: List of functions to apply (from first to last)
    :return: Proxy functor
    """
    def comp(*args, **kwargs):
        res = funcs[0](*args, **kwargs)
        for func in funcs[1:]:
            res = func(res)

        return res

    return comp

def partial(func, *pargs, **pkwargs):
    """
    Performs partial application on `func`

    :param func: function to apply
    :param pargs: default positional parameters
    :param pkwargs: default keyword parameters
    :return: Proxy functor
    """
    def comp(*cargs, **ckwargs):
        # Concatenate positional parameters
        args = pargs + cargs

        # Merge kwargs
        kwargs = pkwargs.copy()
        kwargs.update(ckwargs)

        # Call function
        return func(*args, **kwargs)

    return comp

class AssetsManifest:
    def __init__(self, file):
        with open(file, 'r') as fd:
            manifest = json.load(fd)

        self.base = manifest['base']
        self.tilesets = []


class SourcesManifest:
    pass


class ResourcesManifest:
    pass


class PackageManifest:
    def __init__(self, file):
        with open(file, 'r') as fd:
            pak_manifest = json.load(fd)
            base_path = compose(realpath, dirname)(file)

        append_base_path = partial(join, base_path)

        self.assets = map(compose(append_base_path, AssetsManifest),
                          pak_manifest['assets'])[:]
        self.sources = map(compose(append_base_path, SourcesManifest),
                           pak_manifest['sources'])[:]
        self.resources = map(compose(append_base_path, ResourcesManifest),
                             pak_manifest['resources'])[:]

# Guard agains importing
if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description="Builds the asset bundle")
    args_parser.add_argument('manifest',
                             help="Package manifest (see documentation)")
    args_parser.add_argument('--name',
                             dest='name',
                             type=argparse.FileType('w+'),
                             default='assets.tar.gz',
                             help="Target archive name")
    args = args_parser.parse_args()

    manifest = PackageManifest(args.manifest)
    print(manifest)
