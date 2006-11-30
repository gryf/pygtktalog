# This Python file uses the following encoding: utf-8
"""
Change, apply and save user defined preferences
"""
import sys
import os

import pygtk
import gtk
import gtk.glade

from config import Config
import dialogs

class Preferences:
    def __init__(self):
        self.conf = Config()
        self.conf.load()
        
        self.gladefile = "glade/prefs.glade"
        
        self.glade = gtk.glade.XML(self.gladefile,"prefs")
        dic = {
            "on_button_ejt_clicked"  :self.show_filechooser,
            "on_button_mnt_clicked"  :self.show_dirchooser,
        }
        self.glade.signal_autoconnect(dic)
        
        self.pref = self.glade.get_widget("prefs")
        
        self.tree = self.glade.get_widget("category")
        
        self.desc = self.glade.get_widget("desc")
        
        self.cd = self.glade.get_widget("mnt_entry")
        self.cd.set_text(self.conf.confd['cd'])
        
        self.eject = self.glade.get_widget("ejt_entry")
        self.eject.set_text(self.conf.confd['eject'])
        self.pref.show()
        
    def show_filechooser(self,widget):
        """dialog for choose eject"""
        dialog = gtk.FileChooserDialog(
            title="Choose eject program",
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK
            )
        )
        
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.eject.set_text(dialog.get_filename())
        
        dialog.destroy()
        
    def show_dirchooser(self,widget):
        """dialog for point the mountpoint"""
        dialog = gtk.FileChooserDialog(
            title="Choose mount point",
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
            self.cd.set_text(dialog.get_filename())
        
        dialog.destroy()
        
