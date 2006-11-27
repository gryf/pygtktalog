# This Python file uses the following encoding: utf-8

import pygtk
import gtk

class Qst:
    """Show simple dialog for questions"""
    def __init__(self, title="", message=""):
        self.dialog = gtk.MessageDialog(
            flags   = gtk.DIALOG_DESTROY_WITH_PARENT,
            type    = gtk.MESSAGE_QUESTION,
            buttons = gtk.BUTTONS_OK_CANCEL,
        )
        self.dialog.set_title(title)
        self.dialog.set_markup(message)
    def run(self):
        retval = self.dialog.run()
        self.dialog.destroy()
        if retval == gtk.RESPONSE_OK:
            return True
        return False

class Inf:
    """Show simple dialog for notices"""
    def __init__(self, title="", message=""):
        self.dialog = gtk.MessageDialog(
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
    def __init__(self, title="", message=""):
        self.dialog = gtk.MessageDialog(
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
    def __init__(self, title="", message=""):
        self.dialog = gtk.MessageDialog(
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

class Abt:
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

class InputDiskLabel:
    """Sepcific dialog for quering user for a disc label""" #{{{
    def __init__(self, label=""):
        self.gladefile = "glade/dialogs.glade"
        self.label = ""
        if label!= None:
            self.label = label
        
    def run(self):
        gladexml = gtk.glade.XML(self.gladefile, "inputDialog")
        dialog = gladexml.get_widget("inputDialog")
        entry = gladexml.get_widget("volname")
        entry.set_text(self.label)
        result = dialog.run()
        dialog.destroy()
        if result == gtk.RESPONSE_OK:
            return entry.get_text()
        return None
        #}}}
