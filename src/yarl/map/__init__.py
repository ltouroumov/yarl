from yarl.map.chunk import ChunkLoader, ChunkTree
from yarl.schema import RegionTable, LevelTable, WorldTable
from sfml import sf


class World:
    def __init__(self, name, save_file):
        """
        Creates an empty world
        """
        self.id = None
        self.save_file = save_file
        self.name = name
        self.size = sf.Vector2(16, 16)
        self.regions = dict()

    def __repr__(self):
        return "World(%s, size: %i by %i)" % (self.name, self.size.x, self.size.y)

    def save(self):
        self.save_file.upsert(WorldTable, self)

    def region(self, name):
        """
        Get a dungeon floor
        """
        if name not in self.regions:
            region = Region(name=name,
                            size=self.size,
                            world_id=self.id,
                            save_file=self.save_file)
            region.save()
            self.regions[name] = region

        return self.regions[name]


class Region:
    """
    Create an unpopulated region
    """
    def __init__(self, name, size, world_id, save_file):
        self.id = None
        self.world_id = world_id
        self.name = name
        self.save_file = save_file
        self.size = size
        self.levels = dict()

    def __repr__(self):
        return "Region(%s, %s levels)" % (self.name, len(self.levels))

    def save(self):
        self.save_file.upsert(RegionTable, self)

    def level(self, name):
        if name not in self.levels:
            level = Level(name=name,
                          size=self.size,
                          region_id=self.id,
                          save_file=self.save_file)
            level.save()
            self.levels[name] = level

        return self.levels[name]


class Level:
    def __init__(self, name, size, region_id, save_file):
        """
        Creates an unpopulated dungeon floor
        """
        self.id = None
        self.region_id = region_id
        self.name = name
        self.size = size
        self.save_file = save_file
        self.loaded = False
        self.loader = None
        self.chunks = None

    def __repr__(self):
        return "Level(%s, size: %i by %i)" % (self.name, self.size.x, self.size.y)

    def save(self):
        self.save_file.upsert(LevelTable, self)
        if self.loader is not None:
            self.loader.save()

    def init(self):
        if not self.loaded:
            self.loader = ChunkLoader(level_id=self.id,
                                      save_file=self.save_file)

            self.chunks = ChunkTree(origin=sf.Vector2(0, 0),
                                    size=self.size,
                                    loader=self.loader)
            self.loaded = True

    def get_tile(self, pos):
        self.init()
        return self.chunks.get_tile(pos)

    def set_tile(self, pos, tile):
        self.init()
        self.chunks.set_tile(pos, tile)

    def set_block(self, pos, block):
        self.init()
        self.chunks.get_tile(pos).set_block(block)