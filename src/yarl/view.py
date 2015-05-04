from sfml import sf
from itertools import product


class TileMap(sf.Drawable):
    def __init__(self, size):
        sf.Drawable.__init__(self)
        self.vertices = sf.VertexArray()
        self.size = size

    def update(self, floor, center):
        self.vertices.resize(self.size.x * self.size.y * 4)
        self.vertices.primitive_type = sf.PrimitiveType.QUADS

        p1 = center - (self.size / 2)
        p2 = center + (self.size / 2)
        for pos in [sf.Vector2(x, y) for (x, y) in product(range(p1.y, p2.y), range(p1.x, p2.x))]:
            tile = floor.chunks.get_tile(pos)
            print("tile=", tile)

    def draw(self, target, states):
        target.draw(self.vertices)