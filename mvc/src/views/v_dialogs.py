# This Python file uses the following encoding: utf-8

import gtk

class Qst(object):
    """Show simple dialog for questions
        if "OK" button pressed, return "True"
        "Cancel" button return "False"
    """
    def __init__(self, title="", message="", secondarymsg=""):
        self.dialog = gtk.MessageDialog(
            flags   = gtk.DIALOG_DESTROY_WITH_PARENT,
            type    = gtk.MESSAGE_QUESTION,
            buttons = gtk.BUTTONS_OK_CANCEL,
            message_format = message,
        )
        self.dialog.set_title(title)
        self.dialog.format_secondary_text(secondarymsg)
    def run(self):
        retval = self.dialog.run()
        self.dialog.destroy()
        if retval == gtk.RESPONSE_OK:
            return True
        return False

class Inf(object):
    """Show simple dialog for notices"""
    def __init__(self, title="", message="", secondarymsg=""):
        self.dialog = gtk.MessageDialog(
            flags   = gtk.DIALOG_DESTROY_WITH_PARENT,
            type    = gtk.MESSAGE_INFO,
            buttons = gtk.BUTTONS_OK,
            message_format = message,
        )
        self.dialog.set_title(title)
        self.dialog.format_secondary_text(secondarymsg)
        self.dialog.connect('response', lambda dialog, response: self.ret(response))
        self.dialog.show()
    def ret(self,result):
        self.dialog.destroy()
        return True
    
class Wrn(object):
    """Show simple dialog for warnings"""
    def __init__(self, title="", message="", secondarymsg=""):
        self.dialog = gtk.MessageDialog(
            flags   = gtk.DIALOG_DESTROY_WITH_PARENT,
            type    = gtk.MESSAGE_WARNING,
            buttons = gtk.BUTTONS_CLOSE,
            message_format = message,
        )
        self.dialog.set_title(title)
        self.dialog.format_secondary_text(secondarymsg)
        self.dialog.connect('response', lambda dialog, response: self.ret(response))
        self.dialog.show()
    def ret(self,result):
        self.dialog.destroy()
        return True
    
class Err(object):
    """Show simple dialog for errors"""
    def __init__(self, title="", message="", secondarymsg=""):
        self.dialog = gtk.MessageDialog(
            flags   = gtk.DIALOG_DESTROY_WITH_PARENT,
            type    = gtk.MESSAGE_ERROR,
            buttons = gtk.BUTTONS_CLOSE,
            message_format = message,
        )
        self.dialog.set_title(title)
        self.dialog.format_secondary_text(secondarymsg)
        self.dialog.connect('response', lambda dialog, response: self.ret(response))
        self.dialog.run()
    def ret(self,result):
        self.dialog.destroy()
        return True

class Abt(object):
    """Show simple about dialog"""
    #{{{
    def __init__(self, name=None, ver="", title="", authors=[],licence=""):
        self.dialog = gtk.AboutDialog()
        self.dialog.set_title(title)
        self.dialog.set_version(ver)
        self.dialog.set_license(licence)
        self.dialog.set_name(name)
        self.dialog.set_authors(authors)
        self.dialog.connect('response', lambda dialog, response: self.dialog.destroy())
        self.dialog.show()
    #}}}
    
class InputDiskLabel(object):
    """Sepcific dialog for quering user for a disc label"""
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

class PointDirectoryToAdd(object):
    """Sepcific dialog for quering user for selecting directory to add"""
    def __init__(self,volname='',dirname=''):
        self.gladefile = "glade/dialogs.glade"
        self.gladexml = gtk.glade.XML(self.gladefile, "addDirDialog")
        self.volname = self.gladexml.get_widget("dirvolname")
        self.volname.set_text(volname)
        self.directory = self.gladexml.get_widget("directory")
        self.directory.set_text(dirname)
        self.gladexml.signal_autoconnect({"on_browse_activate":self.show_dirchooser,"on_browse_clicked":self.show_dirchooser})
        
    def show_dirchooser(self,widget):
        """dialog for point the mountpoint"""
        dialog = gtk.FileChooserDialog(
            title="Choose directory to add",
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK
            )
        )
        
        dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.directory.set_text(dialog.get_filename())
        dialog.destroy()
    
    def run(self):
        dialog = self.gladexml.get_widget("addDirDialog")
        ch = True
        result = dialog.run()
        while ch:
            if result == gtk.RESPONSE_OK and (self.volname.get_text()=='' or self.directory.get_text() == ''):
                a = Err("Error - pyGTKtalog","There are fields needed to be filled.","Cannot add directory without path and disc label.")
                ch = True
                result = dialog.run()
            else:
                ch = False
        dialog.destroy()
        if result == gtk.RESPONSE_OK:
            return self.volname.get_text(),self.directory.get_text()
        else:
            return None,None
