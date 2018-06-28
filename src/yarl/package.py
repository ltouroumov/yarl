import itertools
import re
from zipfile import ZipFile
from yarl.util import base_dir, partial
import json
import glob
from collections import namedtuple
import os
from os.path import join, isdir, basename, realpath, relpath
from importlib.abc import *
from importlib.machinery import ModuleSpec
import logging

logger = logging.getLogger(__name__)


class BaseManifest(object):
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

    Tileset = namedtuple('Tileset', ['name', 'texture', 'map'])

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
            index.add_item(PackageIndex.TILESET, name, path)

    def build(self, archive):
        for name, path in self.tilesets():
            archive.write(path, arcname=join('assets', name))


class SourcesManifest(BaseManifest):
    """
    Defines python source files to be packaged
    Sources might be processed before storage
    """

    def __init__(self, file):
        super().__init__(file)
        self.root = realpath(join(self.base, self.manifest['root']))
        self.provides = self.manifest['provides']
        self.bootstrap = self.manifest['bootstrap']

    def sources(self):
        def walk_dir(root, subpath=''):
            for node in os.listdir(root):
                real_path = join(root, node)
                rel_path = join(subpath, node)
                if isdir(real_path):
                    yield from walk_dir(real_path, rel_path)
                else:
                    yield (real_path, rel_path)

        for provides in self.provides:
            base_package = provides.split('.')
            base_path = join(self.root, *base_package)
            for real_path, file in walk_dir(base_path):
                is_package = '__init__.py' in file
                file_package = (file[:-12] if is_package else file[:-3]).split(os.sep)
                package_name = str.join('.', map(str, itertools.chain(base_package, filter(bool, file_package))))

                yield (package_name, is_package, real_path)

    def index(self, index):
        for name, ispkg, path in self.sources():
            index.add_item(PackageIndex.MODULE, name, path, meta={'is_package': ispkg})

        index.add_item(PackageIndex.LOADER, self.name, self.bootstrap)

    def build(self, archive):
        for name, ispkg, path in self.sources():
            source = open(path, 'r').read()
            archive.writestr(join('src', name),
                             data=source)


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
                name = re.sub(r'[\\/]+', '/', join(self.path, relpath(file, self.base)))
                yield (name, file)

    def index(self, index):
        for name, file in self.resources():
            index.add_item(PackageIndex.RESOURCE, name, file)

    def build(self, archive):
        for name, file in self.resources():
            archive.write(file, arcname=name)


class PackageIndex(object):
    """
    Indexes resources inside a package
    Allows test of existence in archive packages and maps keys to files in directory packages
    """
    LOADER = 'loaders'
    MODULE = 'modules'
    TILESET = 'tilesets'
    RESOURCE = 'resources'

    CATEGORIES = [LOADER, MODULE, TILESET, RESOURCE]

    def __init__(self):
        self.data = {category: dict() for category in self.CATEGORIES}

    def add_item(self, kind, name, path, meta=None):
        pool = self.data[kind]
        if name in pool:
            raise KeyError("Duplicate %s key: %s" % (kind, name))

        pool[name] = (path, meta)

    def has_item(self, kind, name):
        return name in self.data[kind]

    def get_item(self, kind, name):
        pool = self.data[kind]
        if name not in pool:
            raise KeyError("Key %s (%s) does not exist" % (name, kind))

        return pool[name]

    def get_all(self, kind):
        for name, data in self.data[kind].items():
            yield name, data

    def load(self, data):
        data = json.loads(data)
        self.data = dict(
            loaders=data['loaders'],
            modules={name: ("src/%s" % name, meta) for name, meta in data['modules'].items()},
            tilesets={name: ("assets/%s" % name, meta) for name, meta in data['tilesets'].items()},
            resources={name: (name, meta) for name, meta in data['resources'].items()},
        )

    @property
    def json(self):
        return json.dumps({'loaders': {name: info for name, info in self.data['loaders'].items()},
                           'modules': {name: meta for name, (path, meta) in self.data['modules'].items()},
                           'tilesets': {name: meta for name, (path, meta) in self.data['tilesets'].items()},
                           'resources': {name: meta for name, (path, meta) in self.data['resources'].items()}})


class PackageManifest(BaseManifest):
    """
    Processes a top-level manifest.json from a package
    """

    def __init__(self, file):
        super().__init__(file)
        self.name = self.manifest['name']

        append_base_path = partial(join, self.base)
        self.packages = [AssetsManifest(file) for file in map(append_base_path, self.manifest['assets'])]
        self.packages += [SourcesManifest(file) for file in map(append_base_path, self.manifest['sources'])]
        self.packages += [ResourcesManifest(file) for file in map(append_base_path, self.manifest['resources'])]

        self.pkindex = PackageIndex()

    def index(self, index):
        for package in self.packages:
            package.index(index)

    def build(self, archive):
        for package in self.packages:
            logger.info("Building %s" % relpath(package.manifest_path, self.base))
            package.index(self.pkindex)
            package.build(archive)

        json = self.pkindex.json
        archive.writestr('index.json', json)

    def build_archive(self, archive_name):
        logger.info("Building manifest %s in %s" % (self.name, self.base))
        with ZipFile(archive_name, mode='w') as archive:
            self.build(archive)

    def build_index(self):
        self.index(self.pkindex)


class BasePackage(object):
    def __init__(self, location):
        self.location = location
        self.index = PackageIndex()

    def load(self):
        """
        This method is responsible for loading the index and other necessary resources
        """
        raise NotImplementedError

    def contains(self, name, kind):
        return self.index.has_item(kind, name)

    def get(self, name, kind):
        return self.index.get_item(kind, name)

    def read(self, name, kind):
        """
        Reads the requested key from the package
        WARNING: Will not call `contains` but will fail silently
        """
        raise NotImplementedError


class ArchivePackage(BasePackage):
    def __init__(self, location):
        super().__init__(location)
        self.archive = None

    def load(self):
        self.archive = ZipFile(self.location, mode='r')

        # Decode and load index
        index = self.archive.read('index.json').decode('utf-8')
        self.index.load(index)

    def read(self, name, kind):
        try:
            arcname, meta = self.index.get_item(kind, name)
            data = self.archive.open(arcname, mode='r')
            return data.read(), meta
        except KeyError:
            raise KeyError("Key %s does not exist in package %s" % (name, self.location))


class DirectoryPackage(BasePackage):
    def load(self):
        manifest = PackageManifest(self.location)
        manifest.index(self.index)

    def read(self, name, kind):
        try:
            path, meta = self.index.get_item(kind, name)
            data = open(path, mode='rb')
            return data.read(), meta
        except KeyError:
            raise KeyError("Key %s does not exist in package %s" % (name, self.location))


class PackageLoader(object):
    def __init__(self, packages):
        self.packages = dict.fromkeys(packages)
        self.class_loader = PackagedClassLoader(self)

    def load(self):
        """
        Load packages definitions from disk
        """

        for name in self.packages:
            if '.json' in name:
                package = DirectoryPackage(name)
            elif '.zip' in name:
                package = ArchivePackage(name)
            else:
                raise RuntimeError("Unhandled package type for %s" % name)

            package.load()
            self.packages[name] = package

        self.class_loader.build()

    def get_from_module(self, name):
        return self.class_loader.get_package(name)

    def dump(self):
        logger.debug("PackageLoader dump")
        for name, pkg in self.packages.items():
            logger.debug("  Package %s (%s)", name, type(pkg).__name__)
            for cat in PackageIndex.CATEGORIES:
                logger.debug("    = %s =", cat)
                for entry, (data, meta) in pkg.index.get_all(cat):
                    logger.debug("    - %s: %s %s", entry, data, repr(meta))

    def hook(self):
        """
        Hook class loader to meta_path
        """
        import sys

        sys.meta_path.append(self.class_loader)


class PackagedClassLoader(MetaPathFinder, ExecutionLoader):
    """
    Implements PEP 302 class loading protocol
    """

    def module_repr(self, module):
        return "<module:%s>" % module.name

    def __init__(self, loader):
        self.loader = loader
        self.modules = dict()

    def build(self):
        """
        Build the package index to allow for fast lookup
        """
        for pkname, package in self.loader.packages.items():
            for module, _ in package.index.get_all(PackageIndex.MODULE):
                self.modules[module] = package

    def find_spec(self, fullname, path, target=None):
        logger.debug("Lookup for %s", fullname)
        if fullname in self.modules:
            return ModuleSpec(fullname, self, is_package=self.is_package(fullname))
        else:
            return None

    def get_source(self, fullname):
        package = self.get_package(fullname)
        source, meta = package.read(fullname, PackageIndex.MODULE)
        return source

    def get_filename(self, fullname):
        package = self.get_package(fullname)
        return "<%s:%s>" % (package.location, fullname)

    def is_package(self, fullname):
        package = self.get_package(fullname)
        filename, meta = package.get(fullname, PackageIndex.MODULE)

        is_package = meta.get('is_package', False)

        return is_package

    def get_package(self, fullname):
        return self.modules[fullname]
