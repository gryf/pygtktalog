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
from pygtktalog.dialogs import About
from pygtktalog.controllers.discs import DiscsController
from pygtktalog.controllers.files import FilesController
#from pygtktalog.controllers.details import DetailsController
#from pygtktalog.controllers.tags import TagcloudController
#from pygtktalog.dialogs import yesno, okcancel, info, warn, error
from pygtktalog.logger import get_logger
from pygtktalog import __version__

LOG = get_logger("main controller")

class MainController(Controller):
    """
    Controller for main application window
    """

    def __init__(self, model, view):
        """
        Initialize MainController, add controllers for trees and details.
        """
        LOG.debug(self.__init__.__doc__.strip())
        Controller.__init__(self, model, view)

        # add controllers for files/tags/details components
        self.discs = DiscsController(model, view.discs)
        self.files = FilesController(model, view.files)
        #self.details = DetailsController(model, view.details)
        #self.tags = TagcloudController(model, view.tags)


    def register_view(self, view):
        """
        Registration view for MainController class
        """
        LOG.debug(self.register_view.__doc__.strip())
        LOG.debug("replace hardcoded defaults with configured!")
        view['main'].set_default_size(800, 600)
        view['hpaned1'].set_position(200)
        view['main'].show()

    def register_adapters(self):
        """
        progress bar/status bar adapters goes here
        """
        LOG.debug(self.register_adapters.__doc__.strip())
        pass

    # signals
    def on_main_destroy_event(self, widget, event):
        """
        Window destroyed. Cleanup before quit.
        """
        LOG.debug(self.on_main_destroy_event.__doc__.strip())
        self.on_quit_activate(widget)
        return True

    def on_quit_activate(self, widget):
        """
        Quit and save window parameters to config file
        """
        LOG.debug(self.on_quit_activate.__doc__.strip())
        #if yesno(_("Do you really want to quit?"),
        #         _("Current database is not saved, any changes will be "
        #           "lost."), _("Quit application") + " - pyGTKtalog", 0):
        self.model.cleanup()
        LOG.debug("quit application")
        gtk.main_quit()
        return False

    def on_about1_activate(self, widget):
        """Show about dialog"""
        About("pyGTKtalog",
              "%s" % __version__,
              "About",
              ["Roman 'gryf' Dobosz"],
              '')
