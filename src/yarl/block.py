from yarl.util import Singleton


@Singleton
class BlockRegistry:
    def __init__(self):
        self.id_map = None
        self.blocks = dict()

    def add(self, klass):
        self.blocks[klass.name] = klass()

    def get(self, name):
        if name in self.blocks:
            return self.blocks[name]
        else:
            raise KeyError("Block %s does not exist" % name)

    def build_map(self):
        next_key = 0
        self.id_map = dict()
        for name in self.blocks:
            self.id_map[next_key] = name
            next_key += 1

    def save_map(self):
        # Packs a tuple
        def pack_pair(pair):
            return "%s:%s" % pair

        pairs = map(pack_pair, self.id_map.items())
        return str.join(";", pairs)

    def load_map(self, data):
        pairs = data.split(';')
        self.id_map = dict()
        for pair in pairs:
            key, val = pair.split(':')
            self.id_map[int(key)] = val

    def get_block_id(self, block):
        name = type(block).name
        res = [blk_id for blk_id, blk_name in self.id_map.items() if blk_name == name]
        if len(res) > 0:
            return res[0]
        else:
            return None

    def from_id(self, block_id):
        if int(block_id) in self.id_map:
            name = self.id_map[int(block_id)]
            return self.blocks[name]
        else:
            raise KeyError("Cannot find block with ID %s" % block_id)


class Block:
    def __init__(self):
        self.icons = dict()

    def register_icons(self, quad):
        pass

    def render(self, meta, vertices):
        raise NotImplemented("Method 'render' must be implemented")


class VoidBlock(Block):
    name = "block.void"

    def register_icons(self, registry):
        self.icons['default'] = registry.add_icon('1:1:objects/Floor.png')

    def render(self, meta, quad):
        quad.set_icon(self.icons['default'])


class FloorBlock(Block):
    name = "block.floor"

    def register_icons(self, registry):
        self.icons['default'] = registry.add_icon('15:4:objects/Floor.png')

    def render(self, meta, quad):
        quad.set_icon(self.icons['default'])


class WallBlock(Block):
    name = "block.wall"

    def register_icons(self, registry):
        self.icons['default'] = registry.add_icon('3:3:objects/Floor.png')

    def render(self, meta, quad):
        quad.set_icon(self.icons['default'])