import sqlite3 as sql
from yarl.schema import SaveSchema
from yarl.map import World


class SaveFile:
    def __init__(self, fpath):
        self.path = fpath
        self.conn = None
        self.schema = None
        self.world = None
        self.is_open = False

    def open(self):
        self.conn = sql.connect(self.path)
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

        print("Saving ...")

    def load(self):
        if not self.is_open:
            raise RuntimeError("Save file not opened")

        if not self.has_schema():
            self.init()

        print("Loading ...")
        res = self.conn.execute("SELECT * FROM worlds WHERE id = 0")
        row = res.fetchone()
        world = World.__new__(World)
        world.id = row["id"]
        world.name = row["name"]

        self.world = world

    def clear(self, name):
        if not self.is_open:
            raise RuntimeError("Save file not opened")

        if not self.has_schema():
            self.init()

        self.schema.clear()
        self.conn.execute("INSERT INTO worlds(id, name) VALUES(0, ?)", (name,))