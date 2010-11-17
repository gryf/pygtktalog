"""
    Project: pyGTKtalog
    Description: Controller for main window
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
import gtk

from gtkmvc import Controller

from pygtktalog.controllers.discs import DiscsController
from pygtktalog.controllers.files import FilesController
#from pygtktalog.controllers.details import DetailsController
#from pygtktalog.controllers.tags import TagcloudController
#from pygtktalog.dialogs import yesno, okcancel, info, warn, error
from pygtktalog.dialogs import open_catalog, save_catalog, error, yesno, about
from pygtktalog.logger import get_logger

LOG = get_logger("main controller")

class MainController(Controller):
    """
    Controller for main application window
    """
    TITLE =  "pyGTKtalog"
    UNTITLED = _("untitled")

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
        if not self.model.tmp_filename:
            view.set_widgets_app_sensitivity(False)
        view['main'].show()

        # status bar
        LOG.debug("register statusbar")
        self.context_id = self.view['mainStatus'].get_context_id('status')
        self.statusbar_id = \
                self.view['mainStatus'].push(self.context_id,
                                             self.model.status_bar_message)


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

    def on_new_activate(self, widget):
        """
        Create new catalog file
        """
        LOG.debug(self.on_new_activate.__doc__.strip())
        self.model.new()
        self._set_title()
        self.view.set_widgets_app_sensitivity(True)

    def on_open_activate(self, widget):
        """
        Open catalog file
        """
        LOG.debug(self.on_open_activate.__doc__.strip())

        if self.model.db_unsaved and 'confirm' in self.model.config and \
                self.model.config['confirm']:
            if not yesno(_("Current database is not saved"),
                         _("Do you really want to open new file and abandon "
                           "current one?"),
                         _("Unsaved data")):
                LOG.debug("Cancel opening catalog file - unsaved data remain")
                return

        initial_path = None
        #if self.model.config.recent and self.model.config.recent[0]:
        #    initial_path = os.path.dirname(self.model.config.recent[0])

        #if not path:
        path = open_catalog(path=initial_path)
        if not path:
            return

        # cleanup files and details
        try:
            self.model.files_list.clear()
        except:
            pass
        #self.__hide_details()
        #self.view['tag_path_box'].hide()
        #buf = self.view['tag_cloud_textview'].get_buffer()
        #buf.set_text('')
        #self.view['tag_cloud_textview'].set_buffer(buf)

        if not self.model.open(path):
            error(_("Cannot open file."),
                  _("File %s cannot be open") % path,
                  _("Error opening file"))
        else:
            #self.__generate_recent_menu()
            #self.__activate_ui(path)
            #self.__tag_cloud()
            self.view.set_widgets_app_sensitivity()
            self._set_title()

        return

    def on_about1_activate(self, widget):
        """Show about dialog"""
        about()

    def on_save_activate(self, widget):
        """
        Save current catalog
        """
        LOG.debug(self.on_save_activate.__doc__.strip())
        if not self.model.cat_fname:
            self.on_save_as_activate(widget)
        else:
            self.model.save()
            self._set_title()

    def on_save_as_activate(self, widget):
        """
        Save current catalog under differnet file
        """
        LOG.debug(self.on_save_as_activate.__doc__.strip())
        initial_path = None
        #if self.model.config.recent[0]:
        #    initial_path = os.path.dirname(self.model.config.recent[0])

        path = save_catalog(path=initial_path)
        if path:
            ret, err = self.model.save(path)
            if ret:
                #self.model.config.add_recent(path)
                self._set_title()
                pass
            else:
                error(_("Cannot write file %s.") % path,
                      "%s" % err,
                      _("Error writing file"))


    # helpers
    def _set_title(self):
        """
        Get title of the main window, to reflect state of the catalog file
        Returns:
            String with apropriate title for main form
        """
        LOG.debug("change the title")

        if not self.model.tmp_filename:
            LOG.debug("application has been initialized, title should"
                      " be empty")
            fname = ""

        elif not self.model.cat_fname:
            fname = self.UNTITLED
        else:
            fname = self.model.cat_fname

        modified = self.model.db_unsaved and "*" or ""

        self.view['main'].set_title("%s%s - %s" % (fname,
                                                   modified, self.TITLE))
