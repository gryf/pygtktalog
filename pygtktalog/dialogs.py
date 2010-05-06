"""
    Project: pyGTKtalog
    Description: Simple dialogs for interact with user
    Type: helper
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-12
"""
import gtk


class Dialog(object):
    """Show simple dialog for questions
        if "OK" button pressed, return "True"
        "Cancel" button return "False"
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
            self.__create_dialog()

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

    def __create_dialog(self):
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
    def __init__(self, name=None, ver="", title="", authors=[],licence=""):
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

