"""
    Project: pyGTKtalog
    Description: Pseudo ORM. Warning. This is a hack.
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-20
"""
from sqlite3 import dbapi2 as sqlite


class SchemaError(Exception):
    """
    Simple class for raising exceptions connected with DataBase class
    """
    pass


class DataBase(object):
    """
    Main class for database common stuff
    """

    schema_order = ["files", "tags", "tags_files", "groups", "thumbnails",
                    "images", "exif", "gthumb"]

    schema = {"files": [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                        ("parent_id", "INTEGER"),
                        ("filename", "TEXT"),
                        ("filepath", "TEXT"),
                        ("date", "datetime"),
                        ("size", "INTEGER"),
                        ("type", "INTEGER"),
                        ("source", "INTEGER"),
                        ("note", "TEXT"),
                        ("description", "TEXT")],
              "tags": [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                       ("group_id", "INTEGER"),
                       ("tag", "TEXT")],
              "tags_files": [("file_id", "INTEGER"),
                             ("tag_id", "INTEGER")],
              "groups": [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                         ("name", "TEXT"),
                         ("color", "TEXT")],
              "thumbnails": [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                             ("file_id", "INTEGER"),
                             ("filename", "TEXT")],
              "images": [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                         ("file_id", "INTEGER"),
                         ("filename", "TEXT")],
              "exif": [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                       ("file_id", "INTEGER"),
                       ("camera", "TEXT"),
                       ("date", "TEXT"),
                       ("aperture", "TEXT"),
                       ("exposure_program", "TEXT"),
                       ("exposure_bias", "TEXT"),
                       ("iso", "TEXT"),
                       ("focal_length", "TEXT"),
                       ("subject_distance", "TEXT"),
                       ("metering_mode", "TEXT"),
                       ("flash", "TEXT"),
                       ("light_source", "TEXT"),
                       ("resolution", "TEXT"),
                       ("orientation", "TEXT")],
              "gthumb": [("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                         ("file_id", "INTEGER"),
                         ("note", "TEXT"),
                         ("place", "TEXT"),
                         ("date", "datetime")]}

    conn = None
    cur = None
    filename = None

    @classmethod
    def get_connection(self):
        """
        Returns: current connection or None if not connected.
        """
        return DataBase.conn

    @classmethod
    def get_cursor(self):
        """
        Returns: current connection cursor, or None if not connected.
        """
        return DataBase.cur

    @classmethod
    def close(self):
        """
        Close current connection. If there is no connection, do nothing.
        Returns: True, if db close was performed, False if there is no
        connection to close.
        """
        if DataBase.cur is None:
            return False

        DataBase.conn.commit()
        DataBase.cur.close()
        DataBase.conn.close()

        DataBase.filename = None
        DataBase.cur = None
        DataBase.conn = None

        return True

    @classmethod
    def open(self, filename=":memory:", force=False):
        """
        Open connection, check database schema, and alternatively create one.

        If provided filename is different from current, current connection is
        closed and new connection is set up.

        Arguments:
            @filename - full path of database file.
            @force - force schema creating.

        Returns: True, if db open succeded, False in other cases.
        """

        if DataBase.filename is not None:
            DataBase.close()

        DataBase.filename = filename

        DataBase.connect()

        if DataBase.cur is None:
            return False

        if not DataBase.check_schema():
            if not force:
                raise SchemaError("Schema for this database is not compatible"
                                  " with pyGTKtalog")
            else:
                # create schema
                DataBase.create_schema(DataBase.cur, DataBase.conn)

        return True

    @classmethod
    def check_schema(self):
        """
        Check schema information.
        Returns: True, if schema is compatible with pyGTKtalog, False
                 otherwise
        """

        if DataBase.cur is None:
            return False

        tables = DataBase.cur.execute("select name, sql from sqlite_master "
                                      "where type='table' and "
                                      "name!='sqlite_sequence'").fetchall()
        table_names = []
        for table in tables:
            table_names.append(str(table[0]))

        table_names.sort()
        orig_tables = DataBase.schema_order[:]
        orig_tables.sort()

        return orig_tables == table_names

    @classmethod
    def create_schema(self, cur, conn):
        """
        Create database schema.
        Returns: True on success, False otherwise
        """
        if cur is None:
            return False

        for tablename in DataBase.schema_order:
            sql = "create table %s(" % tablename
            for column, coltype in DataBase.schema[tablename]:
                sql += "%s %s," % (column, coltype)
            sql = sql[:-1] + ")" # remove last comma and close definition
            #import pdb; pdb.set_trace()
            cur.execute(sql)

        # add initial values
        cur.execute("INSERT INTO files VALUES"
                             "(1, 1, 'root', null, 0, 0, 0, 0, null, null)")

        cur.execute("INSERT INTO groups VALUES(1, 'default',"
                             "'black')")
        conn.commit()
        return True

    @classmethod
    def connect(self):
        """
        Connect to database.
        Returns: cursor for connection.
        """
        if DataBase.cur:
            return DataBase.cur

        types = sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES
        DataBase.conn = sqlite.connect(DataBase.filename, detect_types=types)
        DataBase.cur = DataBase.conn.cursor()
        return DataBase.cur


def create_database():
    DataBase.open(":memory:", True)

