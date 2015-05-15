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

    def by_id(self, block_id):
        res = [blk for name, blk in self.blocks.items() if blk.key == int(block_id)]
        if len(res) > 0:
            return res[0]
        else:
            raise KeyError("Cannot find block with ID %s" % block_id)


class Block:
    def __init__(self, key):
        self.key = key
        self.icons = dict()

    def register_icons(self, registry):
        pass

    def render(self, meta, vertices):
        raise NotImplemented("Method 'render' must be implemented")


class VoidBlock(Block):
    name = "block.void"

    def register_icons(self, registry):
        self.icons['default'] = registry.add_icon('1:1:Objects/Floor.png')

    def render(self, meta, vertices):
        pass


class FloorBlock(Block):
    name = "block.floor"

    def register_icons(self, registry):
        self.icons['default'] = registry.add_icon('15:4:Objects/Floor.png')

    def render(self, meta, vertices):
        pass


class WallBlock(Block):
    name = "block.wall"

    def register_icons(self, registry):
        self.icons['default'] = registry.add_icon('3:3:Objects/Floor.png')

    def render(self, meta, vertices):
        pass