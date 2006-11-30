# This Python file uses the following encoding: utf-8
"""
Change, apply and save user defined preferences
"""
import sys
import os

import pygtk
import gtk
import gtk.glade
import gobject

from config import Config
import dialogs

class Preferences:
    def __init__(self):
        self.category_dict = {'Disk options':'disk_group','General':'general_group','Scan options':'scan_group'}
        self.conf = Config()
        self.conf.load()
        
        self.gladefile = "glade/prefs.glade"
        
        self.glade = gtk.glade.XML(self.gladefile,"prefs")
        dic = {
            "on_button_ejt_clicked"             :self.show_filechooser,
            "on_button_mnt_clicked"             :self.show_dirchooser,
            "on_category_tree_cursor_changed"   :self.activate_pan,
        }
        self.glade.signal_autoconnect(dic)
        
        self.pref = self.glade.get_widget("prefs")
        
        self.desc = self.glade.get_widget("desc")
        
        self.cd = self.glade.get_widget("mnt_entry")
        self.cd.set_text(self.conf.confd['cd'])
        
        self.eject = self.glade.get_widget("ejt_entry")
        self.eject.set_text(self.conf.confd['eject'])
        self.pref.show()
        
        self.tree = self.glade.get_widget("category_tree")
        self.model = gtk.ListStore(gobject.TYPE_STRING)
        self.model.clear()
        self.tree.set_model(self.model)
        self.tree.set_headers_visible(False)
        self.tree.show()
        
        for i in self.category_dict:
            print i,self.category_dict[i]
            myiter = self.model.insert_after(None,None)
            self.model.set_value(myiter,0,i)

        renderer=gtk.CellRendererText()
        column=gtk.TreeViewColumn("Name",renderer, text=0)
        column.set_resizable(True)
        self.tree.append_column(column)
                                
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
        
    def activate_pan(self,treeview):
        model = treeview.get_model()
        selected = model.get_value(model.get_iter(treeview.get_cursor()[0]),0)
        iterator = treeview.get_model().get_iter_first();
        while iterator != None:
            if model.get_value(iterator,0) == selected:
                try:
                    self.glade.get_widget(self.category_dict[model.get_value(iterator,0)]).show()
                except:
                    pass
            else:
                try:
                    self.glade.get_widget(self.category_dict[model.get_value(iterator,0)]).hide()
                except:
                    pass
            iterator = treeview.get_model().iter_next(iterator);
        
if __name__ == "__main__":
    try:
        app=Preferences()
        #app.run()
        gtk.main()
    except KeyboardInterrupt:
        gtk.main_quit
