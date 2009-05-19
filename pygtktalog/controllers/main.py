"""
    Project: pyGTKtalog
    Description: Controller for main window
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
import gtk

from gtkmvc import Controller

from pygtktalog.dialogs import yesno, okcancel, info, warn, error

class MainController(Controller):
    """
    Controller for main application window
    """

    def __init__(self, model, view):
        """Initialize main controller"""
        Controller.__init__(self, model, view)
    
    def register_view(self, view):
        """Default view registration stuff"""
        view['main'].show()

    def register_adapters(self):
        """
        progress bar/status bar adapters goes here
        """
        pass


    def on_quit_activate(self, widget):
        """Quit and save window parameters to config file"""
        # check if any unsaved project is on go.
        #if self.model.unsaved_project and \
        #self.model.config.confd['confirmquit']:
        #    if not yesno.Qst(_("Quit application") + " - pyGTKtalog",
        #                       _("Do you really want to quit?"),
        #                       _("Current database is not saved, any changes "
        #                         "will be lost.")).run():
        #        return
        #self.__store_settings()
        #self.model.cleanup()
        msg1 = _("Do you really want to quit?")
        msg2 = _("Current database is not saved, any changes will be lost.")
        title = _("Quit application") + " - pyGTKtalog"

        if yesno(msg1, msg2, title, 0):
            gtk.main_quit()
        return False
