import tarfile as tar
from sfml import sf
from os.path import basename
from yarl.service import Inject


@Inject(loader='engine.package_loader')
class AssetLoader:
    def __init__(self, loader):
        self.loader = loader

    def load(self):
        for file in self.repo_files:
            print("Loading repository %s" % file)
            name = basename(file)
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

        raise KeyError("File not found %s in asset repositories" % file)


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
