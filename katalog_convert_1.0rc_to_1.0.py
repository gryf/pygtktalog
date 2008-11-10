#!/usr/bin/python
# This Python file uses the following encoding: utf-8
#
#  Author: Roman 'gryf' Dobosz  gryf@elysium.pl
#
#  Copyright (C) 2007 by Roman 'gryf' Dobosz
#
#  This file is part of pyGTKtalog.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

#  -------------------------------------------------------------------------
import sys
import os
import shutil
import tarfile

try:
    import sqlite3 as sqlite
except ImportError:
    from pysqlite2 import dbapi2 as sqlite
from datetime import datetime

class OldModel(object):
    """Create, load, save, manipulate db file which is container for data"""

    def __init__(self):
        """initialize"""
        self.db_cursor = None
        self.db_connection = None
        self.internal_dirname = None

    def cleanup(self):
        """remove temporary directory tree from filesystem"""
        self.__close_db_connection()
        if self.internal_dirname != None:
            try:
                shutil.rmtree(self.internal_dirname)
            except OSError:
                pass
        return

    def open(self, filename=None):
        """try to open db file"""
        self.__create_internal_dirname()
        self.filename = filename

        try:
            tar = tarfile.open(filename, "r:gz")
        except:
            try:
                tar = tarfile.open(filename, "r")
            except:
                self.internal_dirname = None
                return False

        os.chdir(self.internal_dirname)
        try:
            tar.extractall()
            if __debug__:
                print "OldModel 73: extracted tarfile into",
                print self.internal_dirname
        except AttributeError:
            # python 2.4 tarfile module lacks of method extractall()
            directories = []
            for tarinfo in tar:
                if tarinfo.isdir():
                    # Extract directory with a safe mode, so that
                    # all files below can be extracted as well.
                    try:
                        os.makedirs(os.path.join('.', tarinfo.name), 0700)
                    except EnvironmentError:
                        pass
                    directories.append(tarinfo)
                else:
                    tar.extract(tarinfo, '.')

            # Reverse sort directories.
            directories.sort(lambda a, b: cmp(a.name, b.name))
            directories.reverse()

            # Set correct owner, mtime and filemode on directories.
            for tarinfo in directories:
                try:
                    os.chown(os.path.join('.', tarinfo.name),
                             tarinfo.uid, tarinfo.gid)
                    os.utime(os.path.join('.', tarinfo.name),
                             (0, tarinfo.mtime))
                except OSError:
                    if __debug__:
                        print "OldModel 103: open(): setting corrext owner,",
                        print "mtime etc"
        tar.close()
        self.__connect_to_db()
        return True

    # private class functions
    def __connect_to_db(self):
        """initialize db connection and store it in class attributes"""
        self.db_connection = sqlite.connect("%s" % \
                    (self.internal_dirname + '/db.sqlite'),
                    detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.db_cursor = self.db_connection.cursor()
        return

    def __close_db_connection(self):
        """close db conection"""
        if self.db_cursor != None:
            self.db_cursor.close()
            self.db_cursor = None
        if self.db_connection != None:
            self.db_connection.close()
            self.db_connection = None
        return

    def __create_internal_dirname(self):
        """create temporary directory for working thumb/image files and
        database"""
        # TODO: change this stupid rutine into tempfile mkdtemp method
        self.cleanup()
        self.internal_dirname = "/tmp/pygtktalog%d" % \
            datetime.now().microsecond
        try:
            os.mkdir(self.internal_dirname)
        except IOError, (errno, strerror):
            print "OldModel 138: __create_internal_dirname(): ", strerror
        return

def setup_path():
    """Sets up the python include paths to include needed directories"""
    import os.path

    from src.utils.globals import TOPDIR
    sys.path = [os.path.join(TOPDIR, "src")] + sys.path
    return

if __name__ == "__main__":
    """run the stuff"""
    if len(sys.argv) != 3:
        print "Usage: %s old_katalog_filename new_katalog_filename" % \
              sys.argv[0]
        print "All available pictures will be exported aswell, however",
        print "thumbnails without"
        print "images will be lost."
        sys.exit()

    # Directory from where pygtkatalog was invoced. We need it for calculate
    # path for argument (catalog file)
    execution_dir = os.path.abspath(os.path.curdir)

    # Directory, where this files lies. We need it to setup private source
    # paths
    libraries_dir = os.path.dirname(__file__)
    os.chdir(libraries_dir)

    setup_path()

    from shutil import copy

    from utils.img import Img
    from models.m_main import MainModel as NewModel

    model = OldModel()
    new_model = NewModel()
    if not model.open(os.path.join(execution_dir, sys.argv[1])):
        print "cannot open katalog in 1.0RC1 format"
        sys.exit()

    model.db_cursor.execute("""create table
                               images2(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      file_id INTEGER,
                                      filename TEXT);""")

    model.db_cursor.execute("delete from thumbnails")
    result = model.db_cursor.execute("select file_id, filename from images")
    # (id, filename)
    # (4921, u'images/13/39.jpg')
    for row in result.fetchall():
        if row[1] and os.path.exists(os.path.join(model.internal_dirname,
                                                  row[1])):
            im = Img(os.path.join(model.internal_dirname, row[1]),
                     new_model.image_path)
            image = im.save()
            sql = "insert into images2(file_id, filename) values (?, ?)"
            model.db_cursor.execute(sql, (row[0], image))

            model.db_cursor.execute("select id from thumbnails where file_id=?", (row[0], ))
            thumb = model.db_cursor.fetchone()
            if not (thumb and thumb[0]):
                sql = "insert into thumbnails(file_id, filename) values (?, ?)"
                model.db_cursor.execute(sql, (row[0], image))


    model.db_connection.commit()
    model.db_cursor.execute("drop table images")
    model.db_cursor.execute("alter table images2 rename to images")

    copy(os.path.join(model.internal_dirname, 'db.sqlite'),
         os.path.join(execution_dir, sys.argv[2]))
    # remove stuff
    model.cleanup()
