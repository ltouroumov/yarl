from sfml import sf
from itertools import product


class TileIcon:
    def __init__(self, cell, spr):
        self.cell = cell
        self.spr = spr


class TileAtlas:
    def __init__(self, tex_pool, size, order=64):
        self.tex_pool = tex_pool
        self.texture = None
        self.render = None
        self.size = size
        self.order = order
        self.next_id = 0

    def build(self, registry):
        self.render = sf.RenderTexture(self.size.x * self.order, self.size.y * self.order)

        for name, block in registry.blocks.items():
            print("Registering icons for %s" % name)
            block.register_icons(self)

        self.render.display()
        self.texture = self.render.texture

    def add_icon(self, name):
        x, y, path = name.split(':')
        pos = sf.Vector2(int(x), int(y))

        rect = sf.Rectangle(sf.Vector2(pos.x * self.size.x, pos.y * self.size.y),
                            self.size)

        tex = self.tex_pool.get(path)
        spr = sf.Sprite(tex, rect)
        spr.position = self.get_pos(self.next_id)

        self.render.draw(spr)

        icon = TileIcon(self.next_id, spr)
        self.next_id += 1

        return icon

    def get_pos(self, cell):
        tu = cell % self.order
        tv = cell // self.order

        return sf.Vector2(tu * self.size.x, tv * self.size.y)

    def tex(self):
        return self.texture


class TileQuad:
    def __init__(self, vertices, index, size):
        self.size = size
        self.index = index
        self.vertices = vertices

    def vertex(self, idx):
        return self.vertices[self.index + idx]

    def set_position(self, pos):
        rect = sf.Rectangle(sf.Vector2(pos.x * self.size.x,
                                       pos.y * self.size.y),
                            self.size)

        self.vertex(0).position = sf.Vector2(rect.left, rect.top)
        self.vertex(1).position = sf.Vector2(rect.right, rect.top)
        self.vertex(2).position = sf.Vector2(rect.right, rect.bottom)
        self.vertex(3).position = sf.Vector2(rect.left, rect.bottom)

    def set_icon(self, icon):
        pass


class TileMap(sf.Drawable):
    def __init__(self, size, atlas):
        sf.Drawable.__init__(self)
        self.vertices = sf.VertexArray()
        self.size = size
        self.atlas = atlas

    def update(self, floor, center):
        self.vertices.resize(self.size.x * self.size.y * 4)
        self.vertices.primitive_type = sf.PrimitiveType.QUADS

        origin = center - (self.size // 2)
        points = [sf.Vector2(x, y) for (x, y) in product(range(0, self.size.x), range(0, self.size.y))]
        for pos in points:
            # Compute tile position
            tpos = origin + pos
            # Compute vertex slice
            base_idx = pos.x + pos.y * self.size.y * 4

            # Fetch tile & block
            tile = floor.get_tile(tpos)
            block = tile.block

            # Render tile
            quad = TileQuad(self.vertices, base_idx, self.atlas.size)
            quad.set_position(pos)
            block.render(tile.meta, quad)

    def draw(self, target, states):
        states.texture = self.atlas.tex()
        target.draw(self.vertices)