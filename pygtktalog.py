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
try:
    import gtk
except ImportError:
    print "You need to install pyGTK v2.10.x or newer."
    sys.exit(1)


def setup_path():
    """Sets up the python include paths to include needed directories"""
    import os.path

    from src.utils.globals import TOPDIR
    sys.path = [os.path.join(TOPDIR, "src")] + sys.path
    return


def check_requirements():
    """Checks versions and other requirements"""
    import sys
    import gtkmvc
    gtkmvc.require("1.2.0")

    try:
        from models.m_config import ConfigModel
    except ImportError:
        print "Some fundamental files are missing.",
        print "Try runnig pyGTKtalog in his root directory"
        sys.exit(1)

    conf = ConfigModel()
    conf.load()

    try:
        import pygtk
        #tell pyGTK, if possible, that we want GTKv2
        pygtk.require("2.0")
    except ImportError:
        #Some distributions come with GTK2, but not pyGTK
        pass

    try:
        from pysqlite2 import dbapi2 as sqlite
    except ImportError:
        print "pyGTKtalog uses SQLite DB.\nYou'll need to get it and the",
        print "python bindings as well.",
        print "http://www.sqlite.org"
        print "http://initd.org/tracker/pysqlite"
        sys.exit(1)

    if conf.confd['exportxls']:
        try:
            import pyExcelerator
        except ImportError:
            print "WARNING: You'll need pyExcelerator, if you want to export",
            print "DB to XLS format."
            print "http://sourceforge.net/projects/pyexcelerator"

    if conf.confd['thumbs'] and conf.confd['retrive']:
        try:
            import Image
        except ImportError:
            print "WARNING: You'll need Python Imaging Library (PIL), if you",
            print "want to make\nthumbnails!"
    return


def get_parameters():
    """Determine application command line options, return db full pathname"""
    import os
    # if we've got two arguments, shell script passed through command line
    # options: current path and probably filename of compressed collection
    if len(sys.argv) > 2:
        return os.path.join(sys.argv[1], sys.argv[2])
    return False


def main(*args):
    """Main function of module pyGTKtalog"""
    from models.m_main import MainModel
    from ctrls.c_main import MainController
    from views.v_main import MainView

    model = MainModel()
    if args and args[0]:
        model.open(args[0])
    controler = MainController(model)
    view = MainView(controler)

    try:
        gtk.main()
    except KeyboardInterrupt:
        model.config.save()
        model.cleanup()
        gtk.main_quit
    pass
    return

if __name__ == "__main__":
    setup_path()
    check_requirements()
    main(get_parameters())
    pass
