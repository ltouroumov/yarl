import sqlite3 as sql
from yarl.util import make_less


class SchemaTable:
    def create(self, cur):
        klass = type(self)
        fields = ", ".join(map(lambda field: " ".join(field), klass.fields))
        ddl_stmt = "CREATE TABLE %s (%s)" % (klass.table_name, fields)
        print(ddl_stmt)
        try:
            with cur:
                cur.execute(ddl_stmt)
            return True
        except sql.DatabaseError:
            return False

    def insert(self, conn, **kwargs):
        klass = type(self)
        fields = [field for field, data in kwargs]
        ph = ",".join(['?'] * len(fields))
        values = [data for field, data in kwargs]

        dml_stmt = "INSERT INTO %(table)s(%(fields)s) VALUES (%(values)s)" % {'table': klass.table_name,
                                                                              'fields': fields,
                                                                              'values': ph}

        with conn:
            conn.execute(dml_stmt, values)


class MetaTable(SchemaTable):
    table_name = 'metadata'
    depends = None
    fields = (
        ('data_key', 'varchar(128) PRIMARY KEY'),
        ('data_val', 'VARCHAR(128)')
    )


class CharacterTable(SchemaTable):
    table_name = 'characters'
    depends = ['levels']
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('name', 'VARCHAR(128)'),
        ('level_id', 'INTEGER'),
        ('level_x', 'INTEGER'),
        ('level_y', 'INTEGER')
    )


class WorldTable(SchemaTable):
    table_name = 'worlds'
    depends = None
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('name', 'VARCHAR(128)'),
    )

class RegionTable(SchemaTable):
    table_name = 'regions'
    depends = None
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('name', 'VARCHAR(128)'),
        ('size_x', 'INTEGER'),
        ('size_y', 'INTEGER')
    )


class LevelTable(SchemaTable):
    table_name = 'levels'
    depends = ['regions']
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('region_id', 'INTEGER'),
        ('name', 'VARCHAR(128)'),
        ('size_x', 'INTEGER'),
        ('size_y', 'INTEGER')
    )


class ChunkTable(SchemaTable):
    table_name = 'chunks'
    depends = ['levels']
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('level_id', 'INTEGER'),
        ('pos_x', 'INTEGER'),
        ('pos_y', 'INTEGER'),
        ('tiles', 'TEXT')
    )


class EntityTable(SchemaTable):
    table_name = 'entities'
    depends = ['levels']
    fields = (
        ('id', 'INTEGER PRIMARY KEY'),
        ('level_id', 'INTEGER'),
        ('type', 'VARCHAR(128)'),
        ('pos_x', 'INTEGER'),
        ('pos_y', 'INTEGER'),
        ('data', 'TEXT')
    )


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
            table_obj = table()
            table_obj.create(self.conn)

        self.conn.commit()