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
    from models.m_main10rc1 import MainModel
    from models.m_main import MainModel as NewModel

    model = MainModel()
    new_model = NewModel()
    if not model.open(os.path.join(execution_dir, sys.argv[1])):
        print "cannot open katalog in 1.0RC1 format"
        sys.exit()

    model.db_cursor.execute("""create table
                               images2(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      file_id INTEGER,
                                      filename TEXT);""")

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

    model.db_connection.commit()
    model.db_cursor.execute("drop table images")
    model.db_cursor.execute("alter table images2 rename to images")

    copy(os.path.join(model.internal_dirname, 'db.sqlite'),
         os.path.join(execution_dir, sys.argv[2]))
    # remove stuff
    model.cleanup()
