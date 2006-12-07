# This Python file uses the following encoding: utf-8
"""
pytGTKtalog.

A wannabe replacement for excellent gtktalog application.

pyGTKtalog is an application for catalogue/index files on removable media such
a CD or DVD discs, directories on hard disks or network shares.

"""
#{{{ try to import all necessary modules
import sys
import os

try:
    from config import Config
except:
    print "Some fundamental files are missing. try runnig pyGTKtalog in his root directory"
    sys.exit(1)

conf = Config()

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
    print "You need to install pyGTK or GTKv2 ",
    print "or set your PYTHONPATH correctly."
    print "try: export PYTHONPATH=",
    print "/usr/local/lib/python2.2/site-packages/"
    sys.exit(1)

try:
    from pysqlite2 import dbapi2 as sqlite
except:
    print "pyGTKtalog uses SQLite DB.\nYou'll need to get it and the python bindings as well.\nhttp://www.sqlite.org\nhttp://initd.org/tracker/pysqlite"
    sys.exit(1)

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
    
# project modules
from mainwin import PyGTKtalog

if __name__ == "__main__":
    app=PyGTKtalog()
    try:
        app.run()
    except KeyboardInterrupt:
        app.storeSettings()
        app.cur.close()
        app.con.close()
        os.unlink(app.db_tmp_filename)
        gtk.main_quit

