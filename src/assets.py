from zipfile import ZipFile
import argparse
import json
from collections import namedtuple
import os
from os.path import join, isdir, basename, dirname, realpath
import hashlib


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


def hash_file(path):
    checksum = hashlib.sha1()
    with open(path, mode='rb') as fd:
        checksum.update(fd.read(128))

    return checksum.hexdigest()


class BaseManifest:
    def __init__(self, file):
        with open(file, 'r') as fd:
            self.manifest = json.load(fd)
            self.name = basename(file)
            self.base = base_dir(file)

    def build(self, archive, index):
        raise NotImplementedError


class AssetsManifest(BaseManifest):
    """
    Defines game assets to be packaged
    Assets can be optimized during compilation
    """

    Tileset = namedtuple('Tileset', ['name', 'texture', 'size'])

    def __init__(self, file):
        super().__init__(file)
        self.name = self.manifest['name']

        def make_tileset(props):
            return AssetsManifest.Tileset(**props)

        self.tilesets = map(make_tileset, self.manifest['tilesets'])

    def build(self, archive, index):
        for tileset in self.tilesets:
            path = join(self.base, tileset.texture)
            name = '%s.%s' % (self.name, tileset.name)
            archive.write(path, arcname=join('assets', name))
            index.add_tileset(name)


class SourcesManifest(BaseManifest):
    """
    Defines python source files to be packaged
    Sources will be compile()'d before being stored
    """

    def __init__(self, file):
        super().__init__(file)
        self.root = realpath(join(self.base, self.manifest['root']))
        self.base_package = self.manifest['base']
        self.bootstrap = self.manifest['bootstrap']

    def build(self, archive, index):
        base_package = self.base_package.split('.')

        def compile_sources():
            compiled = dict()

            def walk_dir(root, subpath=''):
                for node in os.listdir(root):
                    real_path = join(root, node)
                    rel_path = join(subpath, node)
                    if isdir(real_path):
                        yield from walk_dir(real_path, rel_path)
                    else:
                        yield (real_path, rel_path)

            for path, file in walk_dir(self.root):
                file_package = (file[:-3] if '__init__.py' not in file else file[:-12]).split(os.sep)
                package_name = str.join('.', base_package + list(filter(bool, file_package)))

                yield (package_name, open(path, mode='rb').read())

            return compiled

        for name, source in compile_sources():
            archive.writestr(join('src', name), source)
            index.add_module(name)


class ResourcesManifest(BaseManifest):
    """
    Defines resources files to be packaged
    These files are copied without alterations
    """

    def __init__(self, file):
        super().__init__(file)

    def build(self, archive, index):
        pass


class PackageIndex:
    def __init__(self):
        self.modules = []
        self.tilesets = []
        self.resources = []

    def add_module(self, name):
        if name in self.modules:
            raise KeyError("Duplicate module key")

        self.modules.append(name)

    def add_tileset(self, name):
        if name in self.tilesets:
            raise KeyError("Duplicate tileset key")

        self.tilesets.append(name)

    def add_resource(self, name):
        if name in self.resources:
            raise KeyError("Duplicate resource key")

        self.resources.append(name)

    @property
    def json(self):
        return json.dumps({'modules': self.modules,
                           'tilesets': self.tilesets,
                           'resources': self.resources})


class PackageManifest(BaseManifest):
    def __init__(self, file):
        super().__init__(file)
        self.name = self.manifest['name']

        append_base_path = partial(join, self.base)
        self.packages = [AssetsManifest(file) for file in map(append_base_path, self.manifest['assets'])]
        self.packages += [SourcesManifest(file) for file in map(append_base_path, self.manifest['sources'])]
        self.packages += [ResourcesManifest(file) for file in map(append_base_path, self.manifest['resources'])]

        self.index = PackageIndex()

    def build(self, archive, index):
        raise RuntimeError("Use build_archive on the package manifest")

    def build_archive(self, archive_name):
        print("Building manifest %s in %s" % (self.name, self.base))
        with ZipFile(archive_name, mode='w') as archive:
            for package in self.packages:
                print("Building %s" % package.name)
                package.build(archive, self.index)

            archive.writestr('manifest.json', self.index.json)

# Guard against accidental execution
if __name__ == "__main__":
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
