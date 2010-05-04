"""
    Project: pyGTKtalog
    Description: convert db created with v.1.x into v.2.x
    Type: tool
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-14
"""
import sys
import os
import bz2
import shutil
from tempfile import mkstemp
from sqlite3 import dbapi2 as sqlite
from datetime import datetime

# import db objects just to create schema
from pygtktalog.dbobjects import File, Exif, Group, Gthumb
from pygtktalog.dbobjects import Image, Tag, Thumbnail
from pygtktalog.dbcommon import connect

def create_schema(cur):
    pass


def create_temporary_db_file():
    """create temporary db file"""
    fd, fname = mkstemp()
    os.close(fd)
    return fname

def connect_to_db(filename):
    """initialize db connection and store it in class attributes"""
    db_connection = sqlite.connect(filename, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
    db_cursor = db_connection.cursor()
    return db_connection, db_cursor

def opendb(filename=None):
    """try to open db file"""
    db_tmp_path = create_temporary_db_file()
    compressed = False

    try:
        test_file = open(filename).read(15)
    except IOError:
        os.unlink(db_tmp_path)
        return False

    if test_file == "SQLite format 3":
        db_tmp = open(db_tmp_path, "wb")
        db_tmp.write(open(filename).read())
        db_tmp.close()
    elif test_file[0:10] == "BZh91AY&SY":
        open_file = bz2.BZ2File(filename)
        try:
            curdb = open(db_tmp_path, "w")
            curdb.write(open_file.read())
            curdb.close()
            open_file.close()
            compressed = True
        except IOError:
            # file is not bz2
            os.unlink(db_tmp_path)
            return False
    else:
        os.unlink(db_tmp_path)
        return False

    return connect_to_db(db_tmp_path), db_tmp_path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: %s src_base dst_base" % sys.argv[0]
        exit()

    result = opendb(sys.argv[1])
    if not result:
        print "unable to open src db file"
        exit()

    (src_con, src_c), src_tmpf = result

    shutil.copy(src_tmpf, sys.argv[2])

    # close src db.
    src_c.close()
    src_con.close()
    os.unlink(src_tmpf)

    # create or update shema
    connect(sys.argv[2])

    dst_con = sqlite.connect(sys.argv[2])
    dst_c = dst_con.cursor()

    sql = "select id, date from files"

    for id, date in dst_c.execute(sql).fetchall():
        sql = "update files set date=? where id=?"
        if date and int(date) > 0:
            dst_c.execute(sql, (datetime.fromtimestamp(int(date)), id))
        else:
            dst_c.execute(sql, (None, id))

    sql = "select id, date from gthumb"

    for id, date in dst_c.execute(sql).fetchall():
        sql = "update gthumb set date=? where id=?"
        try:
            if int(date) > 0:
                dst_c.execute(sql, (datetime.fromtimestamp(int(date)), id))
            else:
                dst_c.execute(sql, (None, id))
        except:
            print id, date

    dst_con.commit()
    dst_c.close()
    dst_con.close()
