from zipfile import ZipFile
import argparse
import json
from os.path import realpath, basename, dirname, join


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

base_dir = compose(realpath, dirname)


class BaseManifest:
    def __init__(self, file):
        with open(file, 'r') as fd:
            self.manifest = json.load(fd)
            self.name = basename(file)
            self.base = base_dir(file)

    def build(self, archive):
        raise NotImplementedError


class AssetsManifest(BaseManifest):
    def __init__(self, file):
        super().__init__(file)
        self.tilesets = []

    def build(self, archive):
        pass

class SourcesManifest(BaseManifest):
    def __init__(self, file):
        super().__init__(file)
        self.sources = []

    def build(self, archive):
        pass


class ResourcesManifest(BaseManifest):
    def __init__(self, file):
        super().__init__(file)
        self.resources = []

    def build(self, archive):
        pass


class PackageManifest(BaseManifest):
    def __init__(self, file):
        super().__init__(file)

        append_base_path = partial(join, self.base)

        self.packages = compose(map, list)(compose(append_base_path, AssetsManifest),
                                           self.manifest['assets'])
        self.packages += compose(map, list)(compose(append_base_path, SourcesManifest),
                                            self.manifest['sources'])
        self.packages += compose(map, list)(compose(append_base_path, ResourcesManifest),
                                            self.manifest['resources'])

    def build(self, archive_name):
        print("Building manifest %s in %s" % (self.name, self.base))
        with ZipFile(archive_name, mode='w') as archive:
            for package in self.packages:
                print("Building %s" % package.name)
                package.build(archive)

# Guard agains importing
if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description="Builds the asset bundle")
    args_parser.add_argument('manifest',
                             help="Package manifest (see documentation)")
    args_parser.add_argument('--name',
                             dest='name',
                             default='assets.tar.gz',
                             help="Target archive name")
    args = args_parser.parse_args()

    manifest = PackageManifest(args.manifest)
    manifest.build(args.name)
