import sqlite3 as sql


class SchemaTable:
    def __init__(self, conn):
        self.conn = conn

    def create(self):
        klass = type(self)
        fields = ", ".join(map(lambda field: " ".join(field), klass.fields))
        ddl_stmt = "CREATE TABLE %s (%s)" % (klass.table_name, fields)
        print(ddl_stmt)
        try:
            with self.conn:
                self.conn.execute(ddl_stmt)
            return True
        except sql.DatabaseError:
            return False

    def select(self, **kwargs):
        raise RuntimeError("Table %s does not implement SELECT" % type(self))

    def upsert(self, obj):
        func = self.insert if obj.id is None else self.update
        with self.conn:
            func(obj)

    def update(self, obj):
        self.conn.execute(type(self).update_sql, obj.__dict__)

    def insert(self, obj):
        cur = self.conn.cursor()
        cur.execute(type(self).insert_sql, obj.__dict__)
        obj.id = cur.lastrowid


class MetaTable(SchemaTable):
    table_name = 'metadata'
    depends = None
    fields = (
        ('data_key', 'varchar(128) PRIMARY KEY'),
        ('data_val', 'VARCHAR(128)')
    )

    update_sql = "UPDATE metadata SET data_key = ?, data_val = ?"
    insert_sql = "INSERT INTO metadata VALUES(?, ?)"


class CharacterTable(SchemaTable):
    table_name = 'characters'
    depends = ['levels']
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('name', 'VARCHAR(128)'),
        ('level_id', 'INTEGER'),
        ('size', 'vector2')
    )

    update_sql = ""
    insert_sql = ""


class WorldTable(SchemaTable):
    table_name = 'worlds'
    depends = None
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('name', 'VARCHAR(128)'),
    )

    update_sql = "UPDATE worlds SET name = :name WHERE id = :id"
    insert_sql = "INSERT INTO worlds(name) VALUES (:name)"


class RegionTable(SchemaTable):
    table_name = 'regions'
    depends = None
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('world_id', 'INTEGER'),
        ('name', 'VARCHAR(128)'),
        ('size', 'vector2')
    )

    update_sql = "UPDATE regions SET world_id = :world_id, name = :name, size = :size WHERE id = :id"
    insert_sql = "INSERT INTO regions(world_id, name, size) VALUES (:world_id, :name, :size)"


class LevelTable(SchemaTable):
    table_name = 'levels'
    depends = ['regions']
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('region_id', 'INTEGER'),
        ('name', 'VARCHAR(128)'),
        ('size', 'vector2')
    )

    update_sql = "UPDATE levels SET region_id = :region_id, name = :name, size = :size WHERE id = :id"
    insert_sql = "INSERT INTO levels(region_id, name, size) VALUES (:region_id, :name, :size)"


class ChunkTable(SchemaTable):
    table_name = 'chunks'
    depends = ['levels']
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('level_id', 'INTEGER'),
        ('pos', 'vector2'),
        ('tiles', 'tilematrix')
    )

    update_sql = "UPDATE chunks SET level_id = :level_id, pos = :pos, tiles = :tiles WHERE id = :id"
    insert_sql = "INSERT INTO chunks(level_id, pos, tiles) VALUES (:level_id, :pos, :tiles)"

    def select(self, **kwargs):
        from yarl.map.chunk import Chunk

        with self.conn:
            cur = self.conn.cursor();
            cur.execute("SELECT * FROM chunks WHERE level_id = :level_id AND pos = :pos", kwargs)
            if cur.rowcount > 0:
                row = cur.fetchone()
                chunk = Chunk(row['pos'])
                chunk.id = row['id']
                chunk.tiles = row['tiles']
                return chunk
            else:
                return None


class EntityTable(SchemaTable):
    table_name = 'entities'
    depends = ['levels']
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('level_id', 'INTEGER'),
        ('type', 'VARCHAR(128)'),
        ('pos', 'vector2'),
        ('data', 'pickle')
    )

    update_sql = "UPDATE entities SET level_id = :level_id, type = :type, pos = :pos, data = :data WHERE id = :id"
    insert_sql = "INSERT INTO entities(level_id, type, pos, data) VALUES (:level_id, :type, :pos, :data)"


class SaveSchema:
    tables = [
        MetaTable,
        WorldTable,
        RegionTable,
        LevelTable,
        ChunkTable,
        EntityTable,
    ]

    def __init__(self, conn, version):
        self.conn = conn
        self.version = version

    def is_valid(self, db_tables):
        schema_tables = map(lambda t: t.table_name, type(self).tables)

        for table in schema_tables:
            if table not in db_tables:
                return False

        return True

    def clear(self):
        tables = type(self).tables
        for table in tables:
            self.conn.execute("DELETE FROM %s" % table.table_name)

        self.conn.commit()

    def create(self):
        tables = type(self).tables
        for table in tables:
            print(table.table_name)
            table_obj = table(self.conn)
            table_obj.create()

        self.conn.commit()