from yarl.block import BlockRegistry


class Tile(object):
    def __init__(self, block=None, meta=None):
        if block is None:
            self.block = BlockRegistry.instance().get('block.void')
        else:
            self.block = block

        if meta is None:
            self.meta = {}
        else:
            self.meta = meta

    def render(self):
        return self.block.render(self.meta)

    def set_block(self, block, meta=None):
        self.block = block
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta
