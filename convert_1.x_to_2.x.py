#!/usr/bin/env python
"""
    Project: pyGTKtalog
    Description: convert db created with v.1.x into v.2.x
    Type: tool
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-14
"""
from datetime import datetime
from sqlite3 import dbapi2 as sqlite
from sqlite3 import OperationalError
from tempfile import mkstemp
import bz2
import errno
import os
import shutil
import sys

from sqlalchemy.dialects.sqlite import DATETIME

from pygtktalog.misc import mk_paths, calculate_image_path

PATH1 = os.path.expanduser("~/.pygtktalog/images")
PATH2 = os.path.expanduser("~/.pygtktalog/imgs2")


def mkdir_p(path):
    """Make directories recurively, like 'mkdir -p' command"""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    return path

def get_images_path(cur):
    """
    Calculate the data dir in order:
        - config table
        - old default path
        - new default path
    return first, which contain provided image filename
    """

    image = cur.execute("select filename from images limit 1").fetchone()
    if image and image[0]:
        image = image[0]

    try:
        result = cur.execute("select value from config where "
                             "key='image_path'").fetchone()
        if (result and result[0] and
            os.path.exists(os.path.join(result[0].encode("utf-8"),
                                        image.encode("utf-8")))):
            return result[0]
    except OperationalError:
        # no such table like config. proceed.
        pass

    for path in (PATH1, PATH2):
        if os.path.exists(os.path.join(path, image)):
            return path
    return None

def get_path(cur, image):
    """
    Calculate the data dir in order:
        - config table
        - old default path
        - new default path
    return first, which contain provided image filename
    """
    try:
        result = cur.execute("select value from config where "
                             "key='image_path'").fetchone()
        if (result and result[0] and
            os.path.exists(os.path.join(result[0].encode("utf-8"),
                                        image.encode("utf-8")))):
            return result[0]
    except OperationalError:
        pass

    for path in (PATH1, PATH2):
        if os.path.exists(os.path.join(path, image)):
            return path
    return None

def old_style_image_handle(fname, source_dir, dest_dir):
    """
    Deal with old-style images in DB. There is a flat list under
    ~/.pygtktalog/images/ directory, which should be converted to nested
    structure.
    """

    partial_path = mk_paths(os.path.join(source_dir, fname), dest_dir)

    dest_file = os.path.join(dest_dir, *partial_path)
    dest_thumb = os.path.join(dest_dir, *partial_path) + "_t"

    shutil.copy(os.path.join(source_dir, fname), dest_file)
    shutil.copy(os.path.join(source_dir, fname + "_t"), dest_thumb)
    with open("log.txt", "a") as fobj:
        fobj.write(os.path.join(fname) + "\n")
        fobj.write(os.path.join(fname + "_t\n"))

    return os.path.join(*partial_path), os.path.join(*partial_path) + "_t"


def new_style_image_handle(partial_path, source_dir, dest_dir):
    """
    Deal with old-style images in DB. In the early version directory was
    hardcoded to ~/.pygtktalog/imgs2/, and all the needed files (with the
    paths) should be copied to the new place.
    params:
        partial_path: string holding the relative path to file, for example
                      `de/ad/be/ef.jpg'
        source_dir: path, where at the moment image file resides. Might be the
                    full path, like `/home/user/.pygtktalog/imgs2`
        dest_dir: path (might be relative or absolute), where we want to put
                  the images (i.e. `../foo-images')
    """
    dest_dir = mkdir_p(os.path.join(dest_dir, os.path.dirname(partial_path)))
    base, ext = os.path.splitext(partial_path)
    thumb = os.path.join(source_dir, "".join([base, "_t", ext]))
    filename = os.path.join(source_dir, partial_path)

    shutil.copy(filename, dest_dir)
    shutil.copy(thumb, dest_dir)


def copy_images_to_destination(cursor, image_path, dest):
    """Copy images to dest directory and correct the db entry, if needed"""

    sql = "select id, filename from images"
    update = "update images set filename=? where id=?"
    t_select = "select id from thumbnails where filename=?"
    t_update = "update thumbnails set filename=? where id=?"

    count = -1
    for count, (id_, filename) in enumerate(cursor.execute(sql).fetchall()):
        if not image_path:
            image_path = get_path(cursor, filename)
            if not image_path:
                raise OSError("Image file '%s' not found under data "
                              "directory, aborting" % filename)

        if image_path == PATH1:
            # old style filenames. Flat list.
            fname, tname = old_style_image_handle(filename, image_path, dest)
            cursor.execute(update, (fname, id_))
            for (thumb_id,) in cursor.execute(t_select,
                                              (filename,)).fetchall():
                cursor.execute(t_update, (tname, thumb_id))
        else:
            # new style filenames. nested dirs
            new_style_image_handle(filename, image_path, dest)

    if count > 0:
        print "copied %d files" % (count + 1)

def create_temporary_db_file():
    """create temporary db file"""
    file_descriptor, fname = mkstemp()
    os.close(file_descriptor)
    return fname

def connect_to_db(filename):
    """initialize db connection and store it in class attributes"""
    db_connection = sqlite.connect(filename, detect_types=
                                   sqlite.PARSE_DECLTYPES |
                                   sqlite.PARSE_COLNAMES)
    db_cursor = db_connection.cursor()
    return db_connection, db_cursor

def opendb(filename=None):
    """try to open db file"""
    db_tmp_path = create_temporary_db_file()

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
        except IOError:
            # file is not bz2
            os.unlink(db_tmp_path)
            return False
    else:
        os.unlink(db_tmp_path)
        return False

    return connect_to_db(db_tmp_path), db_tmp_path

def _update_dates(cursor, select_sql, update_sql):
    """update date format - worker function"""
    for id_, date in cursor.execute(select_sql).fetchall():
        try:
            date = int(date)
        except ValueError:
            # most probably there is no need for updating this record.
            continue
        except TypeError:
            date = 0

        if date > 0:
            val = DATETIME().bind_processor(None)(datetime.fromtimestamp(date))
        else:
            val = None
        cursor.execute(update_sql, (val, id_))

def update_dates(cursor):
    """Update date format from plain int to datetime object"""

    _update_dates(cursor,
                  "select id, date from files",
                  "update files set date=? where id=?")
    _update_dates(cursor,
                  "select id, date from gthumb",
                  "update gthumb set date=? where id=?")


def main():
    """Main logic"""
    if len(sys.argv) not in (4, 3):
        print("usage: %s source_dbfile destination_dbfile [image_dir]\n"
              "where image dir is a name where to put images. same name with"
              "'_images' suffix by default"
              % sys.argv[0])
        exit()

    if len(sys.argv) == 4:
        source_dbfile, destination_dbfile, image_dir = sys.argv[1:]
    else:
        source_dbfile, destination_dbfile = sys.argv[1:]
        image_dir = ":same_as_db:"

    result = opendb(source_dbfile)
    if not result:
        print("unable to open src db file")
        exit()

    (connection, cursor), temporary_database_filename = result

    cursor.close()
    connection.close()
    shutil.copy(temporary_database_filename, destination_dbfile)
    os.unlink(temporary_database_filename)

    connection = sqlite.connect(destination_dbfile)
    cursor = connection.cursor()

    if cursor.execute("select name from sqlite_master where type='table' "
                      "and name='table_name'").fetchone() is None:
        cursor.execute("CREATE TABLE 'config' (\n\t'id'\tINTEGER NOT NULL,\n"
                       "\t'key'\tTEXT,\n\t'value'\tTEXT,\n\tPRIMARY "
                       "KEY(id)\n)")

    if cursor.execute("select value from config where "
                      "key='image_path'").fetchone() is None:
        cursor.execute("insert into config(key, value) "
                       "values('image_path', ?)", (image_dir,))
    else:
        cursor.execute("update config set value=? where key='image_path'",
                       (image_dir,))

    if image_dir == ":same_as_db:":
        db_fname = os.path.basename(destination_dbfile)
        base, dummy = os.path.splitext(db_fname)
        image_dir_path = os.path.join(os.path.dirname(destination_dbfile),
                                      base + "_images")
    else:
        image_dir_path = image_dir

    calculate_image_path(image_dir_path, True)

    update_dates(cursor)
    old_image_path = get_images_path(cursor)
    copy_images_to_destination(cursor, old_image_path, image_dir_path)

    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
