"""
    Project: pyGTKtalog
    Description: Simple dialogs for interact with user
    Type: helper
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-12
"""
import os

import gtk


class Dialog(object):
    """
    Show simple dialog for questions
    Returns: Bool - True, if "OK" button pressed, False otherwise.
    """

    def __init__(self, dialog_type, message, secondary_msg="", title=""):
        """
        Initialize some defaults
        """
        self.dialog = None
        self.buttons = gtk.BUTTONS_OK
        self.ok_default = False
        self.message = message
        self.secondary_msg = secondary_msg
        self.type = dialog_type
        self.title = title

    def run(self):
        """Show the dialog"""
        if self.dialog is None:
            self._create_dialog()

        # Change default/focus from cancel/no to ok/yes. Suitable only for
        # Question dialog.
        # Ofcourse, if something changes in the future, this could break
        # things.
        if self.ok_default:
            button = self.dialog.get_children()[0].get_children()[2]
            button.get_children()[self.ok_default].grab_default()

        retval = self.dialog.run()
        self.dialog.destroy()
        if retval == gtk.RESPONSE_OK or retval == gtk.RESPONSE_YES:
            return True
        return False

    def _create_dialog(self):
        """Create MessageDialog widgt"""
        if self.type == gtk.MESSAGE_QUESTION and \
           self.buttons not in (gtk.BUTTONS_YES_NO, gtk.BUTTONS_OK_CANCEL):
            self.buttons = gtk.BUTTONS_YES_NO

        self.dialog = gtk.MessageDialog(buttons=self.buttons, type=self.type,
                                        message_format=self.message)
        self.dialog.format_secondary_text(self.secondary_msg)
        self.dialog.set_title(self.title)

class About(object):
    """
    Show About dialog
    """
    def __init__(self, name=None, ver="", title="", authors=[], licence=""):
        self.dialog = gtk.AboutDialog()
        self.dialog.set_title(title)
        self.dialog.set_version(ver)
        self.dialog.set_license(licence)
        self.dialog.set_name(name)
        self.dialog.set_authors(authors)
        self.dialog.connect('response',
                            lambda dialog, response: self.dialog.destroy())
        self.dialog.show()

# TODO: finish this, re-use Dialog class instead of copy/paste of old classes!
# def about(name, version, )

class ChooseFile(object):
    """
    Common file chooser
    """
    URI = None
    BUTTON_PAIRS = {'cancel': (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL),
                    'ok': (gtk.STOCK_OK, gtk.RESPONSE_APPLY),
                    'save': (gtk.STOCK_SAVE, gtk.RESPONSE_APPLY),
                    'open': (gtk.STOCK_OPEN, gtk.RESPONSE_APPLY)}
    CHOOSER_TYPES = {'open': gtk.FILE_CHOOSER_ACTION_OPEN,
                     'save': gtk.FILE_CHOOSER_ACTION_SAVE}
    FILTERS = {'catalogs': {'name': "Catalog files",
                            'patterns': ("*.sqlite", "*.sqlite.bz2")},
               'all': {'name': "All files", 'patterns': ("*.*",)}}

    def __init__(self, title="", buttons=('cancel', 'ok'), path=None,
                 chooser_type="open"):
        super(ChooseFile, self).__init__()
        self.path = path
        self.title = title
        self.action = self.CHOOSER_TYPES[chooser_type]
        self.buttons=[]
        for button in buttons:
            self.buttons.append(self.BUTTON_PAIRS[button][0])
            self.buttons.append(self.BUTTON_PAIRS[button][1])
        self.buttons = tuple(self.buttons)
        self.confirmation = False
        self.dialog = None
        self.filters = []

    def _mk_dialog(self):
        """
        Create FileChooserDialog object
        """
        self.dialog = gtk.FileChooserDialog(self.title, None, self.action,
                                            self.buttons)
        self.dialog.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        self.dialog.set_default_response(gtk.RESPONSE_OK)
        self.dialog.set_do_overwrite_confirmation(self.confirmation)
        self.dialog.set_title(self.title)

        if self.URI:
            self.dialog.set_current_folder_uri(self.URI)
        elif self.path and os.path.exists(self.path):
            self.path = "file://"+os.path.abspath(self.path)
            self.dialog.set_current_folder_uri(self.path)

        for filtr in self._get_filters():
            self.dialog.add_filter(filtr)

    def _get_filters(self):
        """
        """
        filters = []
        for filter_def in self.filters:
            filtr = gtk.FileFilter()
            filtr.set_name(self.FILTERS[filter_def]['name'])
            for pat in self.FILTERS[filter_def]['patterns']:
                filtr.add_pattern(pat)
            filters.append(filtr)
        return filters

    def run(self):
        """
        Show dialog, get response.
        Returns:

        Returns: String - with filename, None otherwise.
        """

        if self.dialog is None:
            self._mk_dialog()

        response = self.dialog.run()
        filename = None

        if response == gtk.RESPONSE_APPLY:
            filename = self.dialog.get_filename()
            self.__class__.URI = self.dialog.get_current_folder_uri()

        self.dialog.destroy()
        return filename


def yesno(message, secondarymsg="", title="", default=False):
    """Question with yes-no buttons. Returns False on 'no', True on 'yes'"""
    dialog = Dialog(gtk.MESSAGE_QUESTION, message, secondarymsg, title)
    dialog.buttons = gtk.BUTTONS_YES_NO
    dialog.ok_default = default
    return dialog.run()

def okcancel(message, secondarymsg="", title="", default=False):
    """Question with ok-cancel buttons. Returns False on 'cancel', True on
    'ok'"""
    dialog = Dialog(gtk.MESSAGE_QUESTION, message, secondarymsg, title)
    dialog.buttons = gtk.BUTTONS_OK_CANCEL
    dialog.ok_default = default
    return dialog.run()

def info(message, secondarymsg="", title="", button=gtk.BUTTONS_OK):
    """Info dialog. Button defaults to gtk.BUTTONS_OK, but can be changed with
    gtk.BUTTONS_CANCEL, gtk.BUTTONS_CLOSE or gtk.BUTTONS_NONE.
    Always returns True."""
    dialog = Dialog(gtk.MESSAGE_INFO, message, secondarymsg, title)
    dialog.buttons = button
    dialog.run()
    return True

def warn(message, secondarymsg="", title="", button=gtk.BUTTONS_OK):
    """Warning dialog. Button defaults to gtk.BUTTONS_OK, but can be changed
    with gtk.BUTTONS_CANCEL, gtk.BUTTONS_CLOSE or gtk.BUTTONS_NONE.
    Always returns True."""
    dialog = Dialog(gtk.MESSAGE_WARNING, message, secondarymsg, title)
    dialog.buttons = button
    dialog.run()
    return True

def error(message, secondarymsg="", title="", button=gtk.BUTTONS_OK):
    """Error dialog. Button defaults to gtk.BUTTONS_OK, but can be changed with
    gtk.BUTTONS_CANCEL, gtk.BUTTONS_CLOSE or gtk.BUTTONS_NONE.
    Always returns True."""
    dialog = Dialog(gtk.MESSAGE_ERROR, message, secondarymsg, title)
    dialog.buttons = button
    dialog.run()
    return True

def open_catalog(title=_("Open catalog"), path=None):
    """
    Request filename from user to open.
    Returns: string - full path and filename or None
    """
    requester = ChooseFile(title)
    requester.filters = ['catalogs', 'all']
    return requester.run()

def save_catalog(title=_("Open catalog"), path=None):
    """
    Request filename from user for save.
    Returns: string - full path and filename or None
    """
    requester = ChooseFile(title, chooser_type="save")
    requester.filters = ['catalogs', 'all']
    requester.confirmation = True
    return requester.run()
