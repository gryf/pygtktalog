"""
    Project: pyGTKtalog
    Description: View for main window
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
import os.path
import gtk
from gtkmvc import View


class MainView(View):
    """
    Create window from glade file. Note, that glade file is placed in view
    module under glade subdirectory.
    """

    glade = os.path.join(os.path.dirname(__file__), "glade", "main.glade")
    top = "main"

    def __init__(self):
        """
        Initialize view
        """
        View.__init__(self)
        self['tag_path_box'].hide()

    def set_widgets_scan_visibility(self, flag):
        """
        Activate/deactivate selected widgets while scanning is active
        """
        pass

