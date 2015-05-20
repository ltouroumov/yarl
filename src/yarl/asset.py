import os.path as path
import tarfile as tar
from sfml import sf
from zipfile import ZipFile
from yarl.util import base_dir, partial
import json
import glob
from collections import namedtuple
import os
from os.path import join, isdir, basename, realpath, relpath


class BaseManifest:
    def __init__(self, file):
        self.manifest_path = file
        with open(file, 'r') as fd:
            self.manifest = json.load(fd)
            self.name = basename(file)
            self.base = base_dir(file)

    def index(self, index):
        raise NotImplementedError

    def build(self, archive):
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

        self.tilesets_list = list(map(make_tileset, self.manifest['tilesets']))

    def tilesets(self):
        for tileset in self.tilesets_list:
            path = join(self.base, tileset.texture)
            name = '%s.%s' % (self.name, tileset.name)
            yield (name, path)

    def index(self, index):
        for name, path in self.tilesets():
            index.add_tileset(name, path)

    def build(self, archive):
        for name, path in self.tilesets():
            archive.write(path, arcname=join('assets', name))


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

    def sources(self):
        base_package = self.base_package.split('.')

        def walk_dir(root, subpath=''):
            for node in os.listdir(root):
                real_path = join(root, node)
                rel_path = join(subpath, node)
                if isdir(real_path):
                    yield from walk_dir(real_path, rel_path)
                else:
                    yield (real_path, rel_path)

        for real_path, file in walk_dir(self.root):
            file_package = (file[:-3] if '__init__.py' not in file else file[:-12]).split(os.sep)
            package_name = str.join('.', base_package + list(filter(bool, file_package)))

            yield (package_name, real_path)

    def index(self, index):
        for name, path in self.sources():
            index.add_module(name, path)

    def build(self, archive):
        for name, path in self.sources():
            archive.writestr(join('src', name), open(path, 'rb').read())


class ResourcesManifest(BaseManifest):
    """
    Defines resources files to be packaged
    These files are copied without alterations
    """

    def __init__(self, file):
        super().__init__(file)
        self.path = self.manifest['path']
        self.glob = self.manifest['glob']

    def resources(self):
        for pattern in self.glob:
                for file in glob.glob(join(self.base, pattern)):
                    name = join(self.path, relpath(file, self.base))
                    yield (name, file)

    def index(self, index):
        for name, file in self.resources():
            index.add_resource(name, file)

    def build(self, archive):
        for name, file in self.resources():
            archive.write(file, arcname=name)


class PackageIndex:
    def __init__(self):
        self.modules = dict()
        self.tilesets = dict()
        self.resources = dict()

    def add_module(self, name, path):
        if name in self.modules:
            raise KeyError("Duplicate module key")

        self.modules[name] = path

    def add_tileset(self, name, path):
        if name in self.tilesets:
            raise KeyError("Duplicate tileset key")

        self.tilesets[name] = path

    def add_resource(self, name, path):
        if name in self.resources:
            raise KeyError("Duplicate resource key")

        self.resources[name] = path

    @property
    def json(self):
        return json.dumps({'modules': list(self.modules.keys()),
                           'tilesets': list(self.tilesets.keys()),
                           'resources': list(self.resources.keys())})


class PackageManifest(BaseManifest):
    def __init__(self, file):
        super().__init__(file)
        self.name = self.manifest['name']

        append_base_path = partial(join, self.base)
        self.packages = [AssetsManifest(file) for file in map(append_base_path, self.manifest['assets'])]
        self.packages += [SourcesManifest(file) for file in map(append_base_path, self.manifest['sources'])]
        self.packages += [ResourcesManifest(file) for file in map(append_base_path, self.manifest['resources'])]

        self.index = PackageIndex()

    def index(self, index):
        raise RuntimeError("Use build_index on the package manifest")

    def build(self, archive):
        raise RuntimeError("Use build_archive on the package manifest")

    def build_archive(self, archive_name):
        print("Building manifest %s in %s" % (self.name, self.base))
        with ZipFile(archive_name, mode='w') as archive:
            for package in self.packages:
                print("Building %s" % relpath(package.manifest_path, self.base))
                package.index(self.index)
                package.build(archive)

            archive.writestr('manifest.json', self.index.json)

    def build_index(self):
        for package in self.packages:
            package.index(self.index)


class AssetProvider:
    def __init__(self, repo_files):
        self.repo_files = repo_files
        self.repo_tar = dict()

    def load(self):
        for file in self.repo_files:
            print("Loading repository %s" % file)
            name = path.basename(file)
            self.repo_tar[name] = tar.open(file, mode='r:gz')

    def get_file(self, file):
        for name in self.repo_tar:
            try:
                repo = self.repo_tar[name]
                member = repo.getmember(file)
                reader = repo.extractfile(member)
                return reader.read()
            except KeyError:
                # Discard not found exception for individual repositories
                pass

        raise KeyError("File not found %s in asset repositories" % path)


class TexturePool:
    def __init__(self, provider):
        self.provider = provider
        self.textures = dict()

    def get(self, name):
        if name not in self.textures:
            data = self.provider.get_file(name)
            image = sf.Image.from_memory(data)
            self.textures[name] = sf.Texture.from_image(image)

        return self.textures[name]