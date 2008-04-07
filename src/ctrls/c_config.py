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
        'Commands':'commands_group',
    }
    category_order = ['General', 'Disk options', 'Scan options',
    'Files extensions', 'Commands']
    
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
        
        self.__toggle_scan_group()
        
        # initialize tree view
        self.__setup_category_tree()
        
        # initialize models for files extensions
        self.view['ext_choose'].set_model(self.model.ext_list)
        self.view['ext_choose'].set_active(0)
        self.view['extension_tree'].get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.view['config'].show();
        return
    # Podłącz sygnały:

    #################
    # connect signals
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
        self.model.save()
        self.view['config'].destroy()
        return
    
    def on_button_ejt_clicked(self, button):
        self.__show_filechooser()
        return
        
    def on_button_mnt_clicked(self, button):
        self.__show_dirchooser()
        return
        
    def on_ch_retrive_toggled(self, widget):
        self.__toggle_scan_group()
        return
        
    def on_ext_choose_changed(self, widget):
        self.__setup_extension_tree()
        self.view['ext_entry'].set_text('')
        return
        
    def on_ext_add_clicked(self, widget):
        ext = self.view['ext_entry'].get_text().lower()
        if len(ext) == 0:
            Dialogs.Err("Config - pyGTKtalog", "Error", "Extension is empty")
            return
        if self.view['ext_choose'].get_active() == 0:
            if ext not in self.model.confd['img_ext']:
                self.model.confd['img_ext'].append(ext)
                self.model.refresh_ext('img_ext')
        else:
            self.model.confd['mov_ext'].append(ext)
            
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
        
        if self.view['ext_choose'].get_active() == 0:
            n = 'img_ext'
        else:
            n = 'mov_ext'
        
        for i in selection:
            self.model.confd[n].remove(model.get_value(model.get_iter(i), 0))
        
        self.__setup_extension_tree()
        return
    
    ############################
    # private controller methods
    def __setup_extension_tree(self):
        if self.view['ext_choose'].get_active() == 0:
            self.model.refresh_ext('img_ext')
        else:
            self.model.refresh_ext('mov_ext')
            
        self.view['extension_tree'].set_model(self.model.ext_tree)
        
        for i in self.view['extension_tree'].get_columns():
            self.view['extension_tree'].remove_column(i)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Extensions", cell, text=0)
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
            if __debug__:
                print "c_config.py: __show_filechooser()", dialog.get_filename()
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
    
