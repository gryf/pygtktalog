"""
    Project: pyGTKtalog
    Description: Pseudo ORM. Warning. This is a hack.
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-20
"""
import os
from sqlite3 import dbapi2 as sqlite
from tempfile import mkstemp


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
        Open connection, check database schema, if it looks ok, than copy it
        to memory.

        If provided filename is different from current, current connection is
        closed and new connection is set up.

        Arguments:
            @filename - full path of database file.
            @force - force schema creating.

        Returns: cursor, if db open succeded, False in other cases.
        """

        if DataBase.filename is not None:
            DataBase.close()

        DataBase.filename = filename

        DataBase.__connect()

        if DataBase.cur is None:
            return False

        if not DataBase.check_schema():
            if not force:
                raise SchemaError("Schema for this database is not compatible"
                                  " with pyGTKtalog")
            else:
                # create schema
                DataBase.__create_schema(DataBase.cur, DataBase.conn)

        if not DataBase.__copy_to_memory():
            return False

        return DataBase.cur

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
    def __create_schema(self, cur, conn):
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
    def __connect(self):
        """
        Connect to database.
        Returns: cursor for connection.
        """
        types = sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES
        DataBase.conn = sqlite.connect(DataBase.filename, detect_types=types)
        DataBase.cur = DataBase.conn.cursor()
        return DataBase.cur

    @classmethod
    def __copy_to_memory(self):
        """
        Copy database to :memory:
        Returns: True if succeded, False otherwise
        """
        if DataBase.cur is None:
            return False

        if not DataBase.check_schema():
            return False

        types = sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES
        mem_conn = sqlite.connect(":memory:", detect_types=types)
        mem_cur = mem_conn.cursor()

        DataBase.__create_schema(mem_cur, mem_conn)

        # copy data
        for tablename in DataBase.schema_order:
            if tablename in ('files', 'groups'):
                sql = "select * from %s where id!=1" % tablename
            else:
                sql = "select * from %s" % tablename
            data = DataBase.cur.execute(sql).fetchall()

            cols = 0

            if data and data[0] and data[0][0]:
                cols = (len(data[0]) * "?,")[:-1]

            sql = "insert into %s values(%s)" % (tablename, cols)

            for row in data:
                mem_cur.execute(sql, row)

        # update sequences
        seqs = DataBase.cur.execute("select name, seq from "
                                    "sqlite_sequence").fetchall()

        for seq in seqs:
            sql = "update sqlite_sequence set seq=? where name=?"
            mem_cur.execute(sql, (seq[1], seq[0]))

        mem_conn.commit()

        DataBase.conn.commit()
        DataBase.cur.close()
        DataBase.conn.close()

        DataBase.cur = mem_cur
        DataBase.conn = mem_conn

        return True

    @classmethod
    def __copy_to_file(self):
        """
        Copy database from :memory:
        Returns: True if succeded, False otherwise
        """
        if DataBase.cur is None:
            return False

        file_desc, dbfilename = mkstemp()
        os.close(file_desc)

        types = sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES
        file_conn = sqlite.connect(dbfilename, detect_types=types)
        file_cur = file_conn.cursor()

        DataBase.__create_schema(file_cur, file_conn)

        # copy data
        for tablename in DataBase.schema_order:
            if tablename in ('files', 'groups'):
                sql = "select * from %s where id!=1" % tablename
            else:
                sql = "select * from %s" % tablename
            data = DataBase.cur.execute(sql).fetchall()

            cols = 0

            if data and data[0] and data[0][0]:
                cols = (len(data[0]) * "?,")[:-1]

            sql = "insert into %s values(%s)" % (tablename, cols)

            for row in data:
                file_cur.execute(sql, row)

        # update sequences
        seqs = DataBase.cur.execute("select name, seq from "
                                    "sqlite_sequence").fetchall()

        for name, seq in seqs:
            sql = "update sqlite_sequence set seq=? where name=?"
            file_cur.execute(sql, (seq, name))

        file_conn.commit()
        file_cur.close()
        file_conn.close()

        return dbfilename


def create_database():
    DataBase.open(":memory:", True)

