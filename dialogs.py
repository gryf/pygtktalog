# This Python file uses the following encoding: utf-8

import pygtk
import gtk

class Qst:
    """Show simple dialog for questions"""
    def __init__(self, win = None, title="", message=""):
        self.dialog = gtk.MessageDialog(
            parent  = None,
            flags   = gtk.DIALOG_DESTROY_WITH_PARENT,
            type    = gtk.MESSAGE_QUESTION,
            buttons = gtk.BUTTONS_OK_CANCEL,
        )
        self.dialog.set_title(title)
        self.dialog.set_markup(message)
        self.dialog.connect('response', lambda dialog, response: self.ret(response))
        self.dialog.show()
    def ret(self,result):
        self.dialog.destroy()
        if result == gtk.RESPONSE_OK:
            return True
        else:
            return False

class Inf:
    """Show simple dialog for notices"""
    def __init__(self, win = None, title="", message=""):
        self.dialog = gtk.MessageDialog(
            parent  = None,
            flags   = gtk.DIALOG_DESTROY_WITH_PARENT,
            type    = gtk.MESSAGE_INFO,
            buttons = gtk.BUTTONS_OK,
        )
        self.dialog.set_title(title)
        self.dialog.set_markup(message)
        self.dialog.connect('response', lambda dialog, response: self.ret(response))
        self.dialog.show()
    def ret(self,result):
        self.dialog.destroy()
        return True

class Wrn:
    """Show simple dialog for warnings"""
    def __init__(self, win = None, title="", message=""):
        self.dialog = gtk.MessageDialog(
            parent  = None,
            flags   = gtk.DIALOG_DESTROY_WITH_PARENT,
            type    = gtk.MESSAGE_WARNING,
            buttons = gtk.BUTTONS_CLOSE,
        )
        self.dialog.set_title(title)
        self.dialog.set_markup(message)
        self.dialog.connect('response', lambda dialog, response: self.ret(response))
        self.dialog.show()
    def ret(self,result):
        self.dialog.destroy()
        return True
            
class Err:
    """Show simple dialog for errors"""
    def __init__(self, win = None, title="", message=""):
        self.dialog = gtk.MessageDialog(
            parent  = None,
            flags   = gtk.DIALOG_DESTROY_WITH_PARENT,
            type    = gtk.MESSAGE_ERROR,
            buttons = gtk.BUTTONS_CLOSE,
        )
        self.dialog.set_title(title)
        self.dialog.set_markup(message)
        self.dialog.connect('response', lambda dialog, response: self.ret(response))
        self.dialog.show()
    def ret(self,result):
        self.dialog.destroy()
        return True

class About:
    """Show simple dialog for errors"""
    def __init__(self, name=None, ver="", title="", authors=[],licence=""):
        self.dialog = gtk.AboutDialog()
        self.dialog.set_title(title)
        self.dialog.set_version(ver)
        self.dialog.set_license(licence)
        self.dialog.set_name(name)
        self.dialog.set_authors(authors)
        self.dialog.connect('response', lambda dialog, response: self.dialog.destroy())
        self.dialog.show()

