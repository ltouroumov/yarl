__author__ = 'jdavid'


class BlockRegistry:
    def __init__(self):
        self.blocks = dict()

    def add(self, klass):
        self.blocks[klass.id] = klass()

    def get(self, name):
        if name in self.blocks:
            return self.blocks[name]
        else:
            raise KeyError("Block %s does not exist" % name)


class Block:
    pass


class VoidBlock(Block):
    id = "block.void"

    def __init__(self):
        pass


class FloorBlock(Block):
    id = "block.floor"

    def __init__(self):
        pass


class WallBlock(Block):
    id = "block.wall"

    def __init__(self):
        pass