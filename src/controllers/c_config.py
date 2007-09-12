# This Python file uses the following encoding: utf-8
import utils._importer
import utils.globals
from gtkmvc import Controller

import gtk

class ConfigController(Controller):
    category_dict = {'Disk options':'disk_group','General':'general_group','Scan options':'scan_group'}
    category_order = ['General','Disk options','Scan options']
    
    def __init__(self, model):
        Controller.__init__(self, model)
        return
    
    def register_view(self, view):
        Controller.register_view(self, view)
        
        # get data from Config object and put it into view
        self.view['mnt_entry'].set_text(self.model.confd['cd'])
        self.view['ejt_entry'].set_text(self.model.confd['ejectapp'])
        self.view['ch_win'].set_active(self.model.confd['savewin'])
        self.view['ch_pan'].set_active(self.model.confd['savepan'])
        self.view['ch_eject'].set_active(self.model.confd['eject'])
        self.view['ch_xls'].set_active(self.model.confd['exportxls'])
        self.view['ch_quit'].set_active(self.model.confd['confirmquit'])
        self.view['ch_wrnmount'].set_active(self.model.confd['mntwarn'])
        self.view['ch_warnnew'].set_active(self.model.confd['confirmabandon'])
        self.view['ch_thumb'].set_active(self.model.confd['pil'])
        self.view['ch_exif'].set_active(self.model.confd['exif'])
        self.view['ch_gthumb'].set_active(self.model.confd['gthumb'])
        
        # initialize tree view
        self.__setup_category_tree()
        self.view['config'].show();
        return
    # Podłącz sygnały:

    #################
    # connect signals
    def on_category_tree_cursor_changed(self, tree):
        """change view to selected row corresponding to group of properties"""
        model = tree.get_model()
        selected = model.get_value(model.get_iter(tree.get_cursor()[0]),0)
        iterator = tree.get_model().get_iter_first();
        while iterator != None:
            if model.get_value(iterator,0) == selected:
                self.view[self.category_dict[model.get_value(iterator,0)]].show()
                self.view['desc'].set_markup("<b>%s</b>" % selected)
            else:
                self.view[self.category_dict[model.get_value(iterator,0)]].hide()
            iterator = tree.get_model().iter_next(iterator);
        return
    
    def on_cancelbutton_clicked(self, button):
        self.view['config'].destroy()
        return
    
    def on_okbutton_clicked(self, button):
        # get data from view and put it into Config object
        self.model.confd['cd'] = self.view['mnt_entry'].get_text()
        self.model.confd['ejectapp'] = self.view['ejt_entry'].get_text()
        self.model.confd['savewin'] = self.view['ch_win'].get_active()
        self.model.confd['savepan'] = self.view['ch_pan'].get_active()
        self.model.confd['eject'] = self.view['ch_eject'].get_active()
        self.model.confd['exportxls'] = self.view['ch_xls'].get_active()
        self.model.confd['confirmquit'] = self.view['ch_quit'].get_active()
        self.model.confd['mntwarn'] = self.view['ch_wrnmount'].get_active()
        self.model.confd['confirmabandon'] = self.view['ch_warnnew'].get_active()
        self.model.confd['pil'] = self.view['ch_thumb'].get_active()
        self.model.confd['exif'] = self.view['ch_exif'].get_active()
        self.model.confd['gthumb'] = self.view['ch_gthumb'].get_active()
        self.model.save()
        self.view['config'].destroy()
        return
    
    def on_button_ejt_clicked(self,button):
        self.__show_filechooser()
        return
        
    def on_button_mnt_clicked(self,button):
        self.__show_dirchooser()
        return
    
    ############################
    # private controller methods
    def __setup_category_tree(self):
        category_tree = self.view['category_tree']
        category_tree.set_model(self.model.category_tree)
        
        self.model.category_tree.clear()
        for i in ['General','Disk options','Scan options']:
            myiter = self.model.category_tree.insert_before(None,None)
            self.model.category_tree.set_value(myiter,0,i)
        
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name",cell,text=0)
        column.set_resizable(True)
        category_tree.append_column(column)
        
    def __show_filechooser(self):
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
            print dialog.get_filename()
            self.view['ejt_entry'].set_text(dialog.get_filename())
        
        dialog.destroy()
        
    def __show_dirchooser(self):
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
        dialog.set_filename(self.view['mnt_entry'].get_text())
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.view['mnt_entry'].set_text(dialog.get_filename())
        dialog.destroy()
        
    pass # end of class
'''
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
        self.category_order = ['General','Disk options','Scan options']
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
        self.pref.set_title("Preferences - pyGTKtalog")
        self.desc = self.glade.get_widget("desc")
        
        self.cd = self.glade.get_widget("mnt_entry")
        self.cd.set_text(self.conf.confd['cd'])
        
        self.eject = self.glade.get_widget("ejt_entry")
        self.eject.set_text(self.conf.confd['ejectapp'])
        
        self.ch_win = self.glade.get_widget("ch_win")
        self.ch_win.set_active(self.conf.confd['savewin'])
        self.ch_pan = self.glade.get_widget("ch_pan")
        self.ch_pan.set_active(self.conf.confd['savepan'])
        self.ch_eject = self.glade.get_widget("ch_eject")
        self.ch_eject.set_active(self.conf.confd['eject'])
        self.ch_xls = self.glade.get_widget("ch_xls")
        self.ch_xls.set_active(self.conf.confd['exportxls'])
        self.ch_quit = self.glade.get_widget("ch_quit")
        self.ch_quit.set_active(self.conf.confd['confirmquit'])
        self.ch_wrnmount = self.glade.get_widget("ch_wrnmount")
        self.ch_wrnmount.set_active(self.conf.confd['mntwarn'])
        self.ch_warnnew = self.glade.get_widget("ch_warnnew")
        self.ch_warnnew.set_active(self.conf.confd['confirmabandon'])        
        
        self.ch_thumb = self.glade.get_widget("ch_thumb")
        self.ch_thumb.set_active(self.conf.confd['pil'])
        self.ch_exif = self.glade.get_widget("ch_exif")
        self.ch_exif.set_active(self.conf.confd['exif'])
        self.ch_gthumb = self.glade.get_widget("ch_gthumb")
        self.ch_gthumb.set_active(self.conf.confd['gthumb'])
        
        self.tree = self.glade.get_widget("category_tree")
        self.model = gtk.ListStore(gobject.TYPE_STRING)
        self.model.clear()
        self.tree.set_model(self.model)
        self.tree.set_headers_visible(False)
        self.tree.show()
        
        for i in self.category_order:
            myiter = self.model.insert_before(None,None)
            self.model.set_value(myiter,0,i)

        renderer=gtk.CellRendererText()
        column=gtk.TreeViewColumn("Name",renderer, text=0)
        column.set_resizable(True)
        self.tree.append_column(column)
        if self.pref.run() == gtk.RESPONSE_OK:
            self.conf.confd['cd'] = self.cd.get_text()
            self.conf.confd['ejectapp'] = self.eject.get_text()
            self.conf.confd['savewin'] = self.ch_win.get_active()
            self.conf.confd['savepan'] = self.ch_pan.get_active()
            self.conf.confd['eject'] = self.ch_eject.get_active()
            self.conf.confd['pil'] = self.ch_thumb.get_active()
            self.conf.confd['exif'] = self.ch_exif.get_active()
            self.conf.confd['gthumb'] = self.ch_gthumb.get_active()
            self.conf.confd['exportxls'] = self.ch_xls.get_active()
            self.conf.confd['confirmquit'] = self.ch_quit.get_active()
            self.conf.confd['mntwarn'] = self.ch_wrnmount.get_active()
            self.conf.confd['confirmabandon'] = self.ch_warnnew.get_active()
            self.conf.save()
        self.pref.destroy()
        
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
        dialog.set_filename(self.conf.confd['cd'])
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
                self.glade.get_widget(self.category_dict[model.get_value(iterator,0)]).show()
                self.desc.set_markup("<b>%s</b>" % selected)
            else:
                self.glade.get_widget(self.category_dict[model.get_value(iterator,0)]).hide()
            iterator = treeview.get_model().iter_next(iterator);
        
if __name__ == "__main__":
    try:
        app=Preferences()
        gtk.main()
    except KeyboardInterrupt:
        gtk.main_quit
'''