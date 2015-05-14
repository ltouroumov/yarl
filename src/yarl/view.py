from sfml import sf
from itertools import product


class TileAtlas:
    def __init__(self, size, order=64):
        self.texture = sf.Texture()
        self.size = size
        self.order = order
        self.next_id = 0

    def build(self, registry):
        render = sf.RenderTexture(self.size.x * self.order, self.size.y * self.order)

        for name, block in registry.blocks.items():
            block.register_icons(self)

        self.texture = render.texture

    def add_icon(self, tex_name, pos):
        self.next_id += 1

    def tex(self):
        return self.texture


class TileMap(sf.Drawable):
    def __init__(self, size, atlas):
        sf.Drawable.__init__(self)
        self.vertices = sf.VertexArray()
        self.size = size
        self.atlas = atlas

    def update(self, floor, center):
        self.vertices.resize(self.size.x * self.size.y * 4)
        self.vertices.primitive_type = sf.PrimitiveType.QUADS

        origin = center - (self.size / 2)
        points = [sf.Vector2(x, y) for (x, y) in product(range(0, self.size.x), range(0, self.size.y))]
        for pos in points:
            # Compute tile position
            tpos = origin + pos
            # Compute vertex slice
            aslice = pos.x + pos.y * self.size.y * 4
            vslice = slice(aslice, aslice + 5)

            # Fetch tile & block
            tile = floor.chunks.get_tile(tpos)
            block = tile.block

            # Render tile
            self.vertices[vslice] = block.render(tile.meta)

    def draw(self, target, states):
        states.texture = self.atlas.tex()
        target.draw(self.vertices)