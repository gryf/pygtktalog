# This Python file uses the following encoding: utf-8
#
#  Author: Roman 'gryf' Dobosz  gryf@elysium.pl
#
#  Copyright (C) 2007 by Roman 'gryf' Dobosz
#
#  This file is part of pyGTKtalog.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

#  -------------------------------------------------------------------------

import gtk
import os
import utils.globals

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
    def __init__(self, name=None, ver="", title="", authors=[],licence=""):
        self.dialog = gtk.AboutDialog()
        self.dialog.set_title(title)
        self.dialog.set_version(ver)
        self.dialog.set_license(licence)
        self.dialog.set_name(name)
        self.dialog.set_authors(authors)
        self.dialog.connect('response', lambda dialog, response: self.dialog.destroy())
        self.dialog.show()
    
class InputDiskLabel(object):
    """Sepcific dialog for quering user for a disc label"""
    def __init__(self, label=""):
        self.gladefile = os.path.join(utils.globals.GLADE_DIR, "dialogs.glade")
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
        self.gladefile = os.path.join(utils.globals.GLADE_DIR, "dialogs.glade")
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

class ChooseDBFilename(object):
    """Sepcific dialog for quering user for selecting filename for database"""
    def __init__(self):
        self.dialog = gtk.FileChooserDialog(
            title="Save catalog as...",
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE,
                gtk.RESPONSE_OK
            )
        )
        
        self.dialog.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        self.dialog.set_default_response(gtk.RESPONSE_OK)
        self.dialog.set_do_overwrite_confirmation(True)
        self.dialog.set_title('Save catalog to file...')
        
        f = gtk.FileFilter()
        f.set_name("Catalog files")
        f.add_pattern("*.pgt")
        self.dialog.add_filter(f)
        f = gtk.FileFilter()
        f.set_name("All files")
        f.add_pattern("*.*")
        self.dialog.add_filter(f)
        
    def show_dialog(self):
        response = self.dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = self.dialog.get_filename()
            if filename[-4] == '.':
                if filename[-3:].lower() != 'pgt':
                    filename = filename + '.pgt'
                else:
                    filename = filename[:-3] + 'pgt'
            else:
                filename = filename + '.pgt'
            self.dialog.destroy()
            return filename
        else:
            self.dialog.destroy()
            return None
    pass
class LoadDBFile(object):
    """Specific class for displaying openFile dialog. It has veryfication for file existence."""
    def __init__(self):
        self.dialog = gtk.FileChooserDialog(
            title="Open catalog",
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK
            )
        )
        
        self.dialog.set_default_response(gtk.RESPONSE_OK)
        
        f = gtk.FileFilter()
        f.set_name("Catalog files")
        f.add_pattern("*.pgt")
        self.dialog.add_filter(f)
        f = gtk.FileFilter()
        f.set_name("All files")
        f.add_pattern("*.*")
        self.dialog.add_filter(f)
        
    def show_dialog(self):
        response = self.dialog.run()
        filename = None
        if response == gtk.RESPONSE_OK:
            try:
                filename = self.dialog.get_filename()
            except:
                pass
            #self.dialog.destroy()
            return 'ok',filename
        else:
            return 'cancel',None
            
    def run(self):
        res,filename = self.show_dialog()
        ch = True
        while ch:
            if res == 'cancel':
                self.dialog.destroy()
                return None
            try:
                os.stat(filename)
                self.dialog.destroy()
                return filename
            except:
                a = Err("Error - pyGTKtalog","File doesn't exist.","The file that you choose does not exist. Choose another one, or cancel operation.")
                ch = True
                res,filename = self.show_dialog()
