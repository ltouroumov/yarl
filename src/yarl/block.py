from yarl.util import Singleton


@Singleton
class BlockRegistry:
    def __init__(self):
        self.blocks = dict()
        self.next_key = 1

    def add(self, klass):
        self.blocks[klass.name] = klass(self.next_key)
        self.next_key += 1

    def get(self, name):
        if name in self.blocks:
            return self.blocks[name]
        else:
            raise KeyError("Block %s does not exist" % name)


class Block:
    def __init__(self, key):
        self.key = key
        self.icons = dict()

    def register_icons(self, registry):
        pass

    def render(self, meta):
        raise NotImplemented("Method 'render' must be implemented")


class VoidBlock(Block):
    name = "block.void"

    def render(self, meta):
        pass


class FloorBlock(Block):
    name = "block.floor"

    def render(self, meta):
        pass


class WallBlock(Block):
    name = "block.wall"

    def render(self, meta):
        pass