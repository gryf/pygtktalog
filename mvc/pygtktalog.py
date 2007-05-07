# This Python file uses the following encoding: utf-8

def setup_path():
    """Sets up the python include paths to include src"""
    import os.path; import sys

    if sys.argv[0]:
        top_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        sys.path = [os.path.join(top_dir, "src")] + sys.path
        pass
    return

if __name__ == "__main__":
    setup_path()
    
    import sys
    import os
    
    try:
        from models.m_config import ConfigModel
    except:
        print "Some fundamental files are missing. try runnig pyGTKtalog in his root directory"
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
        print "You need to install pyGTK or GTKv2 ",
        print "or set your PYTHONPATH correctly."
        print "try: export PYTHONPATH=",
        print "/usr/local/lib/python2.2/site-packages/"
        sys.exit(1)
    
    try:
        from pysqlite2 import dbapi2 as sqlite
        import mx.DateTime
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
    
    from models.m_main import MainModel
    from controllers.c_main import MainController
    from views.v_main import MainView
    m = MainModel()
    c = MainController(m)
    v = MainView(c)
    
    import gtk
    try:
        gtk.main()
    except KeyboardInterrupt:
        import os
        #c.storeSettings()
        #c.cur.close()
        #c.con.close()
        try:
            os.unlink(c.db_tmp_filename)
        except:
            pass
        gtk.main_quit
    pass
