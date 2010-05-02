"""
    Project: pyGTKtalog
    Description: View for main window
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
import os.path

from gtkmvc import View


def get_glade(glade_filename):
    """
    Return full path to specified glade file
    """
    return os.path.join(os.path.dirname(__file__), "glade", glade_filename)


class MainView(View):
    """
    Create window from glade file. Note, that glade file is placed in view
    module under glade subdirectory.
    """
    glade = get_glade("main.glade")
    top = "main"

    def __init__(self, top="main"):
        """
        Initialize view
        """
        View.__init__(self)
        self['tag_path_box'].hide()
        self.discs = DiscsView()
        self['scrolledwindow1'].add_with_viewport(self.discs.get_top_widget())

    def set_widgets_scan_sensitivity(self, sensitive=True):
        """
        Activate/deactivate selected widgets while scanning is active
        """
        pass


class DiscsView(View):
    """
    Separate Discs TreeView subview.
    """
    glade = get_glade("discs.glade")
    top = 'discs'

    def __init__(self):
        """
        Initialize view
        """
        View.__init__(self)
        self.popup_menu = DiscsPopupView()


class DiscsPopupView(View):
    """
    Separate Discs PopUp subview.
    """
    glade = get_glade("discs.glade")
    top = 'discs_popup'

    def __init__(self):
        """
        Initialize view
        """
        View.__init__(self)


#class FilesView(View):
#    """
#    Separate subview of Files TreeView as a table.
#    """
#    glade = get_glade("files.glade")
#    top = 'files'

#    def __init__(self):
#        """
#        Initialize view
#        """
#        View.__init__(self)


#class TagcloudView(View):
#    """
#    Textview subview with clickable tags.
#    """
#    glade = get_glade("tagcloud.glade")
#    top = 'tag_cloud_textview'

#    def __init__(self):
#        """
#        Initialize view
#        """
#        View.__init__(self)


#class DetailsView(View):
#    """
#    Notebook subview containing tabs with details and possibly Exif, images
#    assocated with object and alternatively thumbnail.
#    """
#    glade = get_glade("details.glade")
#    top = 'notebook_details'

#    def __init__(self):
#        """
#        Initialize view
#        """
#        View.__init__(self)


