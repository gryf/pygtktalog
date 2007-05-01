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
    
    from models.m_main import MainModel
    from controllers.c_main import MainController
    from views.v_main import MainView
    m = MainModel()
    c = MainController(m)
    v = MainView(c)
    
    import gtk
    gtk.main()
    pass
