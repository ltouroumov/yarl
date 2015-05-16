from sfml import sf


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
        self.render.clear()

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

        icon = self.next_id
        self.next_id += 1

        return icon

    def get_pos(self, cell):
        tu = cell % self.order
        tv = cell // self.order

        return sf.Vector2(tu * self.size.x, tv * self.size.y)

    def get_rect(self, cell):
        pos = self.get_pos(cell)
        return sf.Rectangle(pos, self.size)

    def tex(self):
        return self.texture


class TileQuad:
    def __init__(self, vertices, index, atlas):
        self.atlas = atlas
        self.index = index
        self.vertices = vertices

    def vertex(self, idx):
        return self.vertices[self.index + idx]

    def set_position(self, pos):
        rect = sf.Rectangle(sf.Vector2(pos.x * self.atlas.size.x,
                                       pos.y * self.atlas.size.y),
                            self.atlas.size)

        self.vertex(0).position = sf.Vector2(rect.left, rect.top)
        self.vertex(1).position = sf.Vector2(rect.right, rect.top)
        self.vertex(2).position = sf.Vector2(rect.right, rect.bottom)
        self.vertex(3).position = sf.Vector2(rect.left, rect.bottom)

    def set_icon(self, icon):
        rect = self.atlas.get_rect(icon)

        self.vertex(0).tex_coords = sf.Vector2(rect.left, rect.top)
        self.vertex(1).tex_coords = sf.Vector2(rect.right, rect.top)
        self.vertex(2).tex_coords = sf.Vector2(rect.right, rect.bottom)
        self.vertex(3).tex_coords = sf.Vector2(rect.left, rect.bottom)


class TileMap(sf.Drawable):
    def __init__(self, size, atlas):
        sf.Drawable.__init__(self)
        self.vertices = sf.VertexArray()
        self.transform = sf.Transform()
        self.size = size
        self.atlas = atlas

    def update(self, floor, center):
        self.vertices.resize(self.size.x * self.size.y * 4)
        self.vertices.primitive_type = sf.PrimitiveType.QUADS

        origin = center - (self.size // 2)
        for y in range(0, self.size.y):
            for x in range(self.size.x):
                pos = sf.Vector2(x, y)
                # Compute vertex slice
                base_idx = (pos.x + pos.y * self.size.x) * 4

                # Compute tile position
                tpos = origin + pos
                # Fetch tile & block
                tile = floor.get_tile(tpos)
                block = tile.block

                # Render tile
                quad = TileQuad(self.vertices, base_idx, self.atlas)
                quad.set_position(pos)
                # quad.set_icon(0)
                block.render(tile.meta, quad)

    def draw(self, target, states):
        # sf.TransformableDrawable.draw(self, target, states)
        states.transform *= self.transform
        states.texture = self.atlas.tex()
        target.draw(self.vertices, states)