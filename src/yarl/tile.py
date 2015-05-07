from yarl.block import VoidBlock


class Tile:
    def __init__(self, block=None):
        if block is None:
            self.block = VoidBlock()
        else:
            self.block = block

        self.meta = {}