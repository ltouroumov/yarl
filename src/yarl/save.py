import sqlite3 as sql
from sfml import sf
from yarl.block import BlockRegistry
from yarl.map.chunk import TileMatrix
from yarl.util import dump_vec2, load_vec2
from yarl.schema import SaveSchema
from yarl.map import World, Region, Level

sql.register_adapter(sf.Vector2, dump_vec2)
sql.register_converter("vector2", load_vec2)

sql.register_adapter(TileMatrix, TileMatrix.pack)
sql.register_converter("tilematrix", TileMatrix.unpack)


class SaveFile(object):
    def __init__(self, fpath, world_id):
        self.path = fpath
        self.id = world_id
        self.conn = None
        self.schema = None
        self.world = None
        self.is_open = False

    def open(self):
        self.conn = sql.connect(self.path, detect_types=sql.PARSE_DECLTYPES)
        self.conn.row_factory = sql.Row
        self.schema = SaveSchema(self.conn, 1.0)
        self.is_open = True

    def close(self):
        self.conn.close()

    def has_schema(self):
        if not self.is_open:
            raise RuntimeError("Save file not opened")

        try:
            res = map(lambda row: row[0],
                      self.conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'"))

            return self.schema.is_valid(res)
        except sql.DatabaseError:
            return False

    def init(self):
        if not self.is_open:
            raise RuntimeError("Save file not opened")

        print("Creating schema ...")
        self.schema.create()

    def save(self):
        if not self.is_open:
            raise RuntimeError("Save file not opened")

        if not self.has_schema():
            self.init()

        self.world.save()
        for n1, region in self.world.regions.items():
            region.save()
            for n2, level in region.levels.items():
                level.save()

        self.conn.commit()

    def upsert(self, table, obj):
        table(self.conn).upsert(obj)

    def select(self, table, **kwargs):
        return table(self.conn).select(**kwargs)

    def load(self):
        if not self.is_open:
            raise RuntimeError("Save file not opened")

        if not self.has_schema():
            self.init()

        registry = BlockRegistry.instance()

        res = self.conn.execute("SELECT * FROM metadata WHERE data_key = ?", ('block_mappings',))
        row = res.fetchone()
        if row is None:
            registry.build_map()
            self.conn.execute("INSERT INTO metadata(data_key, data_val) VALUES (?, ?)", ('block_mappings',
                                                                                         registry.save_map()))
            self.conn.commit()
        else:
            registry.load_map(row['data_val'])

        res = self.conn.execute("SELECT * FROM worlds WHERE id = ?", (self.id,))
        row = res.fetchone()
        world = World(name=row['name'],
                      save_file=self)
        world.id = row['id']
        world.regions = self.load_regions(self.id)

        self.world = world

    def load_regions(self, world_id):
        res = self.conn.execute("SELECT * FROM regions WHERE world_id = ?", (world_id,))
        regions = dict()
        for row in res.fetchall():
            region = Region(name=row['name'],
                            size=row['size'],
                            world_id=world_id,
                            save_file=self)
            region.id = row['id']
            region.levels = self.load_levels(region.id)
            regions[region.name] = region

        return regions

    def load_levels(self, region_id):
        res = self.conn.execute("SELECT * FROM levels WHERE region_id = ?", (region_id,))
        levels = dict()
        for row in res.fetchall():
            level = Level(name=row['name'],
                          size=row['size'],
                          region_id=region_id,
                          save_file=self)
            level.id = row['id']
            levels[level.name] = level

        return levels

    def clear(self, name):
        if not self.is_open:
            raise RuntimeError("Save file not opened")

        if not self.has_schema():
            self.init()

        self.schema.clear()
        self.conn.execute("INSERT INTO worlds(id, name) VALUES(0, ?)", (name,))
        self.conn.commit()

    def get_chunk(self, pos, level):
        pass