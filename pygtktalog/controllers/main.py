"""
    Project: pyGTKtalog
    Description: Controller for main window
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
import gtk

from gtkmvc import Controller

#from pygtktalog.dialogs import yesno
from pygtktalog.controllers.discs import DiscsController
#from pygtktalog.controllers.files import FilesController
#from pygtktalog.controllers.details import DetailsController
#from pygtktalog.controllers.tags import TagcloudController
#from pygtktalog.dialogs import yesno, okcancel, info, warn, error
from pygtktalog.logger import get_logger

LOG = get_logger("main controller")

class MainController(Controller):
    """
    Controller for main application window
    """

    def __init__(self, model, view):
        """Initialize main controller"""
        Controller.__init__(self, model, view)

        # add controllers for files/tags components
        self.discs = DiscsController(model, view.discs)
        #self.files = FilesController(model, view.files)
        #self.details = DetailsController(model, view.details)
        #self.tags = TagcloudController(model, view.tags)


    def register_view(self, view):
        """Default view registration stuff"""
        # one row contains image and text
        view['main'].show()

    def register_adapters(self):
        """
        progress bar/status bar adapters goes here
        """
        pass

    # signals
    def on_main_destroy_event(self, widget, event):
        """Quit"""
        self.on_quit_activate(widget)
        return True

    def on_quit_activate(self, widget):
        """Quit and save window parameters to config file"""

        #if yesno(_("Do you really want to quit?"),
        #         _("Current database is not saved, any changes will be "
        #           "lost."), _("Quit application") + " - pyGTKtalog", 0):
        self.model.cleanup()
        LOG.debug("quit application")
        gtk.main_quit()
        return False

