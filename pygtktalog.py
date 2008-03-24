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

import gtk

def setup_path():
    """Sets up the python include paths to include needed directories"""
    import os.path
    import sys
    from src.utils.globals import TOPDIR
    sys.path = [os.path.join(TOPDIR, "src")] + sys.path
    return


def check_requirements():
    """Checks versions and other requirements"""
    import gtkmvc; gtkmvc.require("1.2.0")
    
    import sys
    import os
    
    try:
        from models.m_config import ConfigModel
    except:
        print "Some fundamental files are missing. Try runnig pyGTKtalog in his root directory"
        sys.exit(1)
    
    conf = ConfigModel()
    conf.load()
    
    try:
        import pygtk
        #tell pyGTK, if possible, that we want GTKv2
        pygtk.require("2.0")
    except:
        #Some distributions come with GTK2, but not pyGTK
        pass
    try:
        import gtk
        import gtk.glade
    except:
        print "You need to install pyGTK v2.10.x or newer.",
        sys.exit(1)
    
    try:
        from pysqlite2 import dbapi2 as sqlite
    except:
        print "pyGTKtalog uses SQLite DB.\nYou'll need to get it and the python bindings as well.\nhttp://www.sqlite.org\nhttp://initd.org/tracker/pysqlite"
        sys.exit(1)
    #try:
    #    import mx.DateTime
    #except:
    #    print "pyGTKtalog uses Egenix mx.DateTime.\nYou can instal it from your distribution repositry,\nor get it at: http://www.egenix.com"
    #    sys.exit(1)
        
    if conf.confd['exportxls']:
        try:
            import pyExcelerator
        except:
            print "You'll need pyExcelerator, if you want to export DB to XLS format.\nhttp://sourceforge.net/projects/pyexcelerator"
            sys.exit(1)
    
    if conf.confd['pil']:
        try:
            import Image, ImageEnhance
        except:
            print "You'll need Python Imaging Library (PIL), if you want to make thumbnails"
            sys.exit(1)
    return

def get_parameters():
    """Determine application command line options, return db full pathname"""
    import sys, os
    # if we've got two arguments, shell script passed through command line
    # options: current path and probably filename of compressed db
    if len(sys.argv) > 2:
        return os.path.join(sys.argv[1],sys.argv[2])
    return False

def main(*args, **kargs):
    from models.m_main import MainModel
    from ctrls.c_main import MainController
    from views.v_main import MainView
    
    m = MainModel()
    if args and args[0]:
        m.open(args[0])
    c = MainController(m)
    v = MainView(c)
    
    try:
        gtk.main()
    except KeyboardInterrupt:
        import os
        m.config.save()
        m.cleanup()
        gtk.main_quit
    pass
    return

if __name__ == "__main__":
    setup_path()
    check_requirements()
    main(get_parameters())
    pass
