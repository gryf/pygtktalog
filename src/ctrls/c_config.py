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
from gtkmvc import Controller
import views.v_dialogs as Dialogs

import gtk

class ConfigController(Controller):
    category_dict = {
        'Disk options':'disk_group',
        'General':'general_group',
        'Scan options':'scan_group',
        'Files extensions':'ft_group',
    }
    category_order = ['General', 'Disk options', 'Scan options',
    'Files extensions',]
    
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
        self.view['ch_wrndel'].set_active(self.model.confd['delwarn'])
        self.view['ch_warnnew'].set_active(self.model.confd['confirmabandon'])
        self.view['ch_thumb'].set_active(self.model.confd['thumbs'])
        self.view['ch_exif'].set_active(self.model.confd['exif'])
        self.view['ch_gthumb'].set_active(self.model.confd['gthumb'])
        self.view['ch_compress'].set_active(self.model.confd['compress'])
        self.view['ch_retrive'].set_active(self.model.confd['retrive'])
        self.view['ch_imageviewer'].set_active(self.model.confd['imgview'])
        self.view['entry_imv'].set_text(self.model.confd['imgprog'])
        
        self.__toggle_scan_group()
        
        # initialize tree view
        self.__setup_category_tree()
        
        # initialize models for files extensions
        self.view['extension_tree'].get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        #self.view['extension_tree'].set_model(self.model.ext_tree)
        self.__setup_extension_tree()
        
        self.view['config'].show();
        return
    # Podłącz sygnały:

    #################
    # connect signals
    def on_extension_tree_cursor_changed(self, tree):
        model = tree.get_model()
        selected = model.get_value(model.get_iter(tree.get_cursor()[0]), 0)
        ext = self.model.confd['extensions']
        self.view['ext_entry'].set_text(selected)
        self.view['com_entry'].set_text(ext[selected])
        
    def on_category_tree_cursor_changed(self, tree):
        """change view to selected row corresponding to group of properties"""
        model = tree.get_model()
        selected = model.get_value(model.get_iter(tree.get_cursor()[0]), 0)
        iterator = tree.get_model().get_iter_first();
        while iterator != None:
            if model.get_value(iterator, 0) == selected:
                self.view[self.category_dict[model.get_value(iterator, 0)]].show()
                self.view['desc'].set_markup("<b>%s</b>" % selected)
            else:
                self.view[self.category_dict[model.get_value(iterator, 0)]].hide()
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
        self.model.confd['delwarn'] = self.view['ch_wrndel'].get_active()
        self.model.confd['confirmabandon'] = self.view['ch_warnnew'].get_active()
        self.model.confd['thumbs'] = self.view['ch_thumb'].get_active()
        self.model.confd['exif'] = self.view['ch_exif'].get_active()
        self.model.confd['gthumb'] = self.view['ch_gthumb'].get_active()
        self.model.confd['compress'] = self.view['ch_compress'].get_active()
        self.model.confd['retrive'] = self.view['ch_retrive'].get_active()
        self.model.confd['imgview'] = self.view['ch_imageviewer'].get_active()
        self.model.confd['imgprog'] = self.view['entry_imv'].get_text()
        self.model.save()
        self.view['config'].destroy()
    
    def on_button_ejt_clicked(self, button):
        fn = self.__show_filechooser("Choose eject program")
        self.view['ejt_entryentry_imv'].set_text(fn)
        
    def on_button_mnt_clicked(self, button):
        fn = self.__show_filechooser("Choose mount point")
        self.view['mnt_entry'].set_text(fn)
        
    def on_ch_retrive_toggled(self, widget):
        self.__toggle_scan_group()
    
    def on_ch_imageviewer_toggled(self, checkbox):
        state = self.view['ch_imageviewer'].get_active()
        for i in ['label_imv', 'entry_imv', 'button_imv']:
            self.view[i].set_sensitive(state)
            
    def on_button_imv_clicked(self, widget):
        fn = self.__show_filechooser("Choose image viewer")
        self.view['entry_imv'].set_text(fn)
        
    def on_ext_add_clicked(self, widget):
        ext = self.view['ext_entry'].get_text().lower()
        com = self.view['com_entry'].get_text()
        if len(ext) == 0 and len(com) == 0:
            Dialogs.Err("Config - pyGTKtalog", "Error", "Extension and command required")
            return
            
        if len(com) == 0:
            Dialogs.Err("Config - pyGTKtalog", "Error", "Command is empty")
            return
            
        if len(ext) == 0:
            Dialogs.Err("Config - pyGTKtalog", "Error", "Extension is empty")
            return
            
        if ext in self.model.confd['extensions'].keys():
            obj = Dialogs.Qst('Alter extension',
                              'Alter extension?',
                              'Extension "%s" will be altered.' % ext)
            if not obj.run():
                return
        self.model.confd['extensions'][ext] = com
            
        self.__setup_extension_tree()
        return
        
    def on_ext_del_clicked(self, widget):
        model, selection = self.view['extension_tree'].get_selection().get_selected_rows()
        if len(selection) == 0:
            Dialogs.Err("Config - pyGTKtalog", "Error", "No item selected")
            return
        elif len(selection) == 1:
            sufix = ''
        else:
            sufix = "s"
        
        if self.model.confd['delwarn']:
            obj = Dialogs.Qst('Delete extension%s' % sufix,
                              'Delete extension%s?' % sufix,
                              'Object%s will be permanently removed.' % sufix)
            if not obj.run():
                return
        
        for i in selection:
            self.model.confd['extensions'].pop(model.get_value(model.get_iter(i), 0))
        
        self.__setup_extension_tree()
        return
    
    ############################
    # private controller methods
    def __setup_extension_tree(self):
        self.model.refresh_ext()
            
        self.view['extension_tree'].set_model(self.model.ext_tree)
        
        for i in self.view['extension_tree'].get_columns():
            self.view['extension_tree'].remove_column(i)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Extension", cell, text=0)
        column.set_resizable(True)
        self.view['extension_tree'].append_column(column)
        
        column = gtk.TreeViewColumn("Command", cell, text=1)
        column.set_resizable(True)
        self.view['extension_tree'].append_column(column)
        
    def __toggle_scan_group(self):
        for i in ('ch_thumb','ch_exif','ch_gthumb'):
            self.view[i].set_sensitive(self.view['ch_retrive'].get_active())
        return
        
    def __setup_category_tree(self):
        category_tree = self.view['category_tree']
        category_tree.set_model(self.model.category_tree)
        
        self.model.category_tree.clear()
        for i in self.category_order:
            myiter = self.model.category_tree.insert_before(None,None)
            self.model.category_tree.set_value(myiter,0,i)
        
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name",cell,text=0)
        column.set_resizable(True)
        category_tree.append_column(column)
        
    def __show_filechooser(self, title):
        """dialog for choose eject"""
        fn = None
        dialog = gtk.FileChooserDialog(
            title=title,
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
            if __debug__:
                print "c_config.py: __show_filechooser()", dialog.get_filename()
            fn = dialog.get_filename()
        dialog.destroy()
        return fn
        
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
    
