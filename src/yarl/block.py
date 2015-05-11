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


class VoidBlock(Block):
    name = "block.void"


class FloorBlock(Block):
    name = "block.floor"


class WallBlock(Block):
    name = "block.wall"