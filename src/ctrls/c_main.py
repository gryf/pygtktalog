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

__version__ = "0.8"
licence = \
"""
GPL v2
http://www.gnu.org/licenses/gpl.txt
"""

import os.path
from utils import deviceHelper
from gtkmvc import Controller

from c_config import ConfigController
from views.v_config import ConfigView
from models.m_config import ConfigModel

import views.v_dialogs as Dialogs

from views.v_image import ImageView

import gtk
import pango

import datetime

class MainController(Controller):
    """Controller for main application window"""
    scan_cd = False
    widgets = (
               "discs","files",
               'save1','save_as1','cut1','copy1','paste1','delete1','add_cd','add_directory1',
               'tb_save','tb_addcd','tb_find','nb_dirs','description','stat1',
        )
    widgets_all = (
                   "discs","files",
                   'file1','edit1','add_cd','add_directory1','help1',
                   'tb_save','tb_addcd','tb_find','tb_new','tb_open','tb_quit',
                   'nb_dirs','description','stat1',
        )
                            
    widgets_cancel = ('cancel','cancel1')
    
    def __init__(self, model):
        """Initialize controller"""
        Controller.__init__(self, model)
        return

    def register_view(self, view):
        Controller.register_view(self, view)
        
        # Make widget set non active
        for widget in self.widgets:
            self.view[widget].set_sensitive(False)
        
        # Make not active "Cancel" button and menuitem
        for widget in self.widgets_cancel:
            self.view[widget].set_sensitive(False)
            
        # hide "debug" button, if production
        # (i.e. python OT running with -OO option)
        if __debug__:
            self.view['debugbtn'].show()
        else:
            self.view['debugbtn'].hide()
        
        # load configuration/defaults and set it to properties
        self.view['toolbar1'].set_active(self.model.config.confd['showtoolbar'])
        if self.model.config.confd['showtoolbar']:
            self.view['maintoolbar'].show()
        else:
            self.view['maintoolbar'].hide()
        statusbar_state = self.model.config.confd['showstatusbar']
        self.view['status_bar1'].set_active(statusbar_state)
        if self.model.config.confd['showstatusbar']:
            self.view['statusprogress'].show()
        else:
            self.view['statusprogress'].hide()
        self.view['hpaned1'].set_position(self.model.config.confd['h'])
        self.view['vpaned1'].set_position(self.model.config.confd['v'])
        self.view['main'].resize(self.model.config.confd['wx'],
                                 self.model.config.confd['wy'])
        
        # initialize statusbar
        self.context_id = self.view['mainStatus'].get_context_id('detailed res')
        self.statusbar_id = self.view['mainStatus'].push(self.context_id,
                                                         "Idle")
        
        # initialize treeviews
        self.__setup_disc_treeview()
        self.__setup_files_treeview()
        self.__setup_exif_treeview()
        
        # in case passing catalog filename in command line, unlock gui
        if self.model.filename != None:
            self.__activate_ui(self.model.filename)
        
        # generate recent menu
        self.__generate_recent_menu()
        
        # Show main window
        self.view['main'].show();
        return
        
    #########################################################################
    # Connect signals from GUI, like menu objects, toolbar buttons and so on.
    def on_images_item_activated(self, iconview, path):
        model = iconview.get_model()
        iter = model.get_iter(path)
        id = model.get_value(iter, 0)
        ImageView(self.model.get_image_path(id))
        
    def on_rename1_activate(self, widget):
        model, iter = self.view['discs'].get_selection().get_selected()
        name = model.get_value(iter, 1)
        id = model.get_value(iter, 0)
        new_name = Dialogs.InputNewName(name).run()

        if __debug__:
            print "c_main.py: on_rename1_activate(): label:", new_name
            
        if new_name != None and new_name != name:
            self.model.rename(id, new_name)
            self.__set_title(filepath=self.model.filename, modified=True)
            
    def on_rename2_activate(self, widget):
        try:
            selection = self.view['files'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
        except TypeError:
            return

        if len(list_of_paths) != 1:
            return
            
        fid = model.get_value(model.get_iter(list_of_paths[0]),0)
        name = model.get_value(model.get_iter(list_of_paths[0]),1)
        
        new_name = Dialogs.InputNewName(name).run()
        if __debug__:
            print "c_main.py: on_rename1_activate(): label:", new_name
            
        if new_name != None and new_name != name:
            self.model.rename(fid, new_name)
            self.__set_title(filepath=self.model.filename, modified=True)
            
        try:
            path, column = self.view['discs'].get_cursor()
            iter = model.get_iter(path)
            self.model.get_root_entries(model.get_value(iter, 0))
        except TypeError:
            self.model.get_root_entries(1)
            return
        return
    
    def on_tag_cloud_textview_motion_notify_event(self, widget):
        if __debug__:
            print "c_main.py: on_tag_cloud_textview_motion_notify_event():"
        w = self.view['tag_cloud_textview'].get_window(gtk.TEXT_WINDOW_TEXT)
        if w:
            w.set_cursor(None)
            
    def on_main_destroy_event(self, window, event):
        self.__do_quit()
        return True
        
    def on_tb_quit_clicked(self, widget):
        self.__do_quit()
        
    def on_quit1_activate(self, widget):
        self.__do_quit()
    
    def on_new1_activate(self, widget):
        self.__new_db()
        
    def on_tb_new_clicked(self, widget):
        self.__new_db()
        
    def on_add_cd_activate(self, widget):
        self.__add_cd()
        
    def on_tb_addcd_clicked(self, widget):
        self.__add_cd()
        
    def on_add_directory1_activate(self, widget):
        """Show dialog for choose drectory to add from filesystem."""
        self.__add_directory()
        return
        
    def on_about1_activate(self, widget):
        """Show about dialog"""
        Dialogs.Abt("pyGTKtalog", __version__, "About",
                    ["Roman 'gryf' Dobosz"], licence)
        return
        
    def on_preferences_activate(self, widget):
        c = ConfigController(self.model.config)
        v = ConfigView(c)
        return
        
    def on_status_bar1_activate(self, widget):
        """Toggle visibility of statusbat and progress bar."""
        activity = self.view['status_bar1'].get_active()
        self.model.config.confd['showstatusbar'] = activity
        if self.view['status_bar1'].get_active():
            self.view['statusprogress'].show()
        else:
            self.view['statusprogress'].hide()
        
    def on_toolbar1_activate(self, widget):
        """Toggle visibility of toolbar bar."""
        activity = self.view['toolbar1'].get_active()
        self.model.config.confd['showtoolbar'] = activity
        if self.view['toolbar1'].get_active():
            self.view['maintoolbar'].show()
        else:
            self.view['maintoolbar'].hide()
        
    def on_save1_activate(self, widget):
        self.__save()
        
    def on_tb_save_clicked(self, widget):
        self.__save()
        
    def on_save_as1_activate(self, widget):
        self.__save_as()
        
    def on_stat1_activate(self, menu_item):
        self.__show_stats()
        
    def on_statistics1_activate(self, menu_item):
        model = self.view['discs'].get_model()
        try:
            path, column = self.view['discs'].get_cursor()
            selected_iter = self.model.discs_tree.get_iter(path)
        except:
            return
            
        selected_id = self.model.discs_tree.get_value(selected_iter, 0)
        self.__show_stats(selected_id)
        
    def on_tb_open_clicked(self, widget):
        self.__open()
        
    def on_open1_activate(self, widget):
        self.__open()
        
    def on_discs_cursor_changed(self, widget):
        """Show files on right treeview, after clicking the left disc
        treeview."""
        model = self.view['discs'].get_model()
        path, column = self.view['discs'].get_cursor()
        iter = self.model.discs_tree.get_iter(path)
        selected_item = self.model.discs_tree.get_value(iter,0)
        self.model.get_root_entries(selected_item)
        
        self.__get_item_info(selected_item)
        return
        
    def on_discs_row_activated(self, treeview, path, treecolumn):
        """If possible, expand or collapse branch of discs tree"""
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path,False)
        return
        
    def on_images_button_press_event(self, iconview, event):
        try:
            path_and_cell = iconview.get_item_at_pos(int(event.x), int(event.y))
        except TypeError:
            return False
            
        if event.button == 3: # Right mouse button. Show context menu.
            try:
                iconview.select_path(path_and_cell[0])
            except TypeError:
                return False
                
            self.__popup_menu(event, 'img_popup')
            return True
        return False
        
    def on_img_delete_activate(self, menu_item):
        list_of_paths = self.view['images'].get_selected_items()
        model = self.view['images'].get_model()
        iter = model.get_iter(list_of_paths[0])
        id = model.get_value(iter, 0)
        self.model.delete_image(id)
        
        try:
            path, column = self.view['files'].get_cursor()
            model = self.view['files'].get_model()
            iter = model.get_iter(path)
            id = model.get_value(iter, 0)
            self.__get_item_info(id)
        except:
            pass
        
    def on_img_add_activate(self, menu_item):
        self.on_add_image1_activate(menu_item)
        
    def on_discs_button_press_event(self, treeview, event):
        try:
            path, column, x, y = treeview.get_path_at_pos(int(event.x),
                                                          int(event.y))
        except TypeError:
            treeview.get_selection().unselect_all()
            return False
                
        if event.button == 3:
            """Right mouse button. Show context menu."""
            try:
                selection = treeview.get_selection()
                model, list_of_paths = selection.get_selected_rows()
            except TypeError:
                list_of_paths = []
                
            if path not in list_of_paths:
                treeview.get_selection().unselect_all()
                treeview.get_selection().select_path(path)
            
            iter = self.model.discs_tree.get_iter(path)
            if self.model.discs_tree.get_value(iter, 3) == 1:
                # if ancestor is 'root', then activate "update" menu item
                self.view['update1'].set_sensitive(True)
            else:
                self.view['update1'].set_sensitive(False)
            self.__popup_menu(event)
            
    def on_expand_all1_activate(self, menuitem):
        self.view['discs'].expand_all()
        return
        
    def on_collapse_all1_activate(self, menuitem):
        self.view['discs'].collapse_all()
        return
        
    def on_files_button_press_event(self, tree, event):
        try:
            path, column, x, y = tree.get_path_at_pos(int(event.x),
                                                      int(event.y))
        except TypeError:
            tree.get_selection().unselect_all()
            return False
        
        if event.button == 3: # Right mouse button. Show context menu.
            try:
                selection = tree.get_selection()
                model, list_of_paths = selection.get_selected_rows()
            except TypeError:
                list_of_paths = []
                
            if len(list_of_paths) == 0:
                selection.select_path(path[0])
                
            if len(list_of_paths) > 1:
                self.view['add_image1'].set_sensitive(False)
                self.view['rename2'].set_sensitive(False)
            else:
                self.view['add_image1'].set_sensitive(True)
                self.view['rename2'].set_sensitive(True)
            self.__popup_menu(event, 'files_popup')
            return True
            
    def on_files_cursor_changed(self, treeview):
        """Show details of selected file/directory"""
        model, paths = treeview.get_selection().get_selected_rows()
        try:
            itera = model.get_iter(paths[0])
            iter = model.get_iter(treeview.get_cursor()[0])
            selected_item = self.model.files_list.get_value(iter, 0)
            self.__get_item_info(selected_item)
        except:
            if __debug__:
                print "c_main.py: on_files_cursor_changed() insufficient iterator"
        return
    
    def on_files_key_release_event(self, a, event):
        if gtk.gdk.keyval_name(event.keyval) == 'BackSpace':
            d_path, d_column = self.view['discs'].get_cursor()
            if d_path and d_column:
                # easy way
                model = self.view['discs'].get_model()
                child_iter = model.get_iter(d_path)
                parent_iter = model.iter_parent(child_iter)
                if parent_iter:
                    self.view['discs'].set_cursor(model.get_path(parent_iter))
                else:
                    # hard way
                    f_model = self.view['files'].get_model()
                    first_iter = f_model.get_iter_first()
                    first_child_value = f_model.get_value(first_iter, 0)
                    # get two steps up
                    value = self.model.get_parent_discs_value(first_child_value)
                    parent_value = self.model.get_parent_discs_value(value)
                    iter = self.model.discs_tree.get_iter_first()
                    while iter:
                        current_value = self.model.discs_tree.get_value(iter,0)
                        if current_value == parent_value:
                            path = self.model.discs_tree.get_path(iter)
                            self.view['discs'].set_cursor(path)
                            iter = None
                        else:
                            iter = self.model.discs_tree.iter_next()
                
    def on_files_row_activated(self, files_obj, row, column):
        """On directory doubleclick in files listview dive into desired
        branch."""
        f_iter = self.model.files_list.get_iter(row)
        current_id = self.model.files_list.get_value(f_iter,0)
        
        if self.model.files_list.get_value(f_iter,4) == 1:
            # ONLY directories. files are omitted.
            self.model.get_root_entries(current_id)
            
            d_path, d_column = self.view['discs'].get_cursor()
            if d_path!=None:
                if not self.view['discs'].row_expanded(d_path):
                    self.view['discs'].expand_row(d_path,False)
            
            iter = self.model.discs_tree.get_iter(d_path)
            new_iter = self.model.discs_tree.iter_children(iter)
            if new_iter:
                while new_iter:
                    current_value = self.model.discs_tree.get_value(new_iter,0)
                    if current_value == current_id:
                        path = self.model.discs_tree.get_path(new_iter)
                        self.view['discs'].set_cursor(path)
                    new_iter = self.model.discs_tree.iter_next(new_iter)
        return
        
    def on_cancel1_activate(self, widget):
        self.__abort()
        
    def on_cancel_clicked(self, widget):
        self.__abort()
        
    def on_tb_find_clicked(self, widget):
        # TODO: implement searcher
        return
        
    def recent_item_response(self, path):
        self.__open(path)
        return
        
    def on_add_tag1_activate(self, menu_item):
        print self.view['files'].get_cursor()
        
    def on_add_image1_activate(self, menu_item):
        images = Dialogs.LoadImageFile().run()
        if not images:
            return
        for image in images:
            try:
                selection = self.view['files'].get_selection()
                model, list_of_paths = selection.get_selected_rows()
                id = model.get_value(model.get_iter(list_of_paths[0]),0)
            except:
                try:
                    path, column = self.view['files'].get_cursor()
                    model = self.view['files'].get_model()
                    iter = model.get_iter(path)
                    id = model.get_value(iter, 0)
                except:
                    return
            self.model.add_image(image, id)
        self.__get_item_info(id)
        return
        
    def on_update1_activate(self, menu_item):
        """Update disc under cursor position"""
        path, column = self.view['discs'].get_cursor()
        model = self.view['discs'].get_model()
        
        # determine origin label and filepath
        filepath, label = self.model.get_label_and_filepath(path)
        
        fid = model.get_value(model.get_iter(path), 0)
        
        if self.model.get_source(path) == self.model.CD:
            self.__add_cd(label, fid)
                
        elif self.model.get_source(path) == self.model.DR:
            self.__add_directory(filepath, label, fid)
                
        return
        
    def on_delete2_activate(self, menu_item):
        try:
            selection = self.view['discs'].get_selection() 
            model, selected_iter = selection.get_selected()
        except:
            return
            
        if self.model.config.confd['delwarn']:
            name = model.get_value(selected_iter, 1)
            obj = Dialogs.Qst('Delete %s' % name, 'Delete %s?' % name,
                              'Object will be permanently removed.')
            if not obj.run():
                return
                
        # remove from model
        path = model.get_path(selected_iter)
        current_id = self.model.discs_tree.get_value(selected_iter, 0)
        model.remove(selected_iter)
        selection.select_path(path)
        
        if not selection.path_is_selected(path):
            row = path[0]-1
            if row >= 0:
                selection.select_path((row,))
                path = (row, )
                
        # delete from db
        self.model.delete(current_id)
                
        # refresh files treeview
        current_id = model.get_value(model.get_iter(path), 0)
        self.model.get_root_entries(current_id)
        
        # refresh file info view
        self.__get_item_info(current_id)
                
        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        return
        
    def on_delete3_activate(self, menu_item):
        dmodel = self.model.discs_tree
        try:
            selection = self.view['files'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
        except TypeError:
            return

        if self.model.config.confd['delwarn']:
            obj = Dialogs.Qst('Delete elements', 'Delete items?',
                              'Items will be permanently removed.')
            if not obj.run():
                return
        
        def foreach_disctree(zmodel, zpath, ziter, d):
            if d[0] == zmodel.get_value(ziter, 0):
                d[1].append(zpath)
            return False
            
        for p in list_of_paths:
            val = model.get_value(model.get_iter(p), 0)
            if model.get_value(model.get_iter(p), 4) == self.model.DIR:
                # remove from disctree model aswell
                dpath = []
                dmodel.foreach(foreach_disctree, (val, dpath))
                for dp in dpath:
                    dmodel.remove(dmodel.get_iter(dp))
                
            # delete from db
            self.model.delete(val)
            
        try:
            selection = self.view['discs'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
            if not list_of_paths:
                list_of_paths = [1]
            self.model.get_root_entries(model.get_value(model.get_iter(list_of_paths[0]),0))
        except TypeError:
            return
        
        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        return

    def on_debugbtn_clicked(self, widget):
        """Debug. To remove in stable version, including button in GUI"""
        if __debug__:
            print "\nc_main.py: on_debugbtn_clicked()"
            print "------"
            print "unsaved_project = %s" % self.model.unsaved_project
            print "filename = %s" % self.model.filename
            print "internal_filename = %s" % self.model.internal_dirname
            print "db_connection = %s" % self.model.db_connection
            print "abort = %s" % self.model.abort
            print "self.model.config.recent = %s" % self.model.config.recent
            print "source: %s" % self.model.source
            
    #####################
    # observed properetis
    def property_statusmsg_value_change(self, model, old, new):
        if self.statusbar_id != 0:
            self.view['mainStatus'].remove(self.context_id, self.statusbar_id)
        self.statusbar_id = self.view['mainStatus'].push(self.context_id,
                                                         "%s" % new)
        return
        
    def property_busy_value_change(self, model, old, new):
        if new != old:
            for w in self.widgets_all:
                self.view[w].set_sensitive(not new)
            for widget in self.widgets_cancel:
                self.view[widget].set_sensitive(new)
            if not new and self.scan_cd:
                self.scan_cd = False
                # umount/eject cd
                ejectapp = self.model.config.confd['ejectapp']
                if self.model.config.confd['eject'] and ejectapp:
                    msg = deviceHelper.eject_cd(ejectapp,
                                                self.model.config.confd['cd'])
                    if msg != 'ok':
                        Dialogs.Wrn("error ejecting device - pyGTKtalog",
                                    "Cannot eject device pointed to %s" %
                                    self.model.config.confd['cd'],
                                    "Last eject message:\n%s" % msg)
                else:
                    msg = deviceHelper.volumount(self.model.config.confd['cd'])
                    if msg != 'ok':
                        Dialogs.Wrn("error unmounting device - pyGTKtalog",
                                    "Cannot unmount device pointed to %s" %
                                    self.model.config.confd['cd'],
                                    "Last umount message:\n%s" % msg)
        return
    
    def property_progress_value_change(self, model, old, new):
        self.view['progressbar1'].set_fraction(new)
        return
        
    #########################
    # private class functions
    def __open(self, path=None):
        """Open catalog file"""
        confirm = self.model.config.confd['confirmabandon']
        if self.model.unsaved_project and confirm:
            obj = Dialogs.Qst('Unsaved data - pyGTKtalog','There is not saved database','Pressing "Ok" will abandon catalog.')
            if not obj.run():
                return
        
        if not path:
            path = Dialogs.LoadDBFile().run()
        
        if path:
            if not self.model.open(path):
                Dialogs.Err("Error opening file - pyGTKtalog","Cannot open \
                            file %s." % path)
            else:
                self.__generate_recent_menu()
                self.__activate_ui(path)
        return
        
    def __save(self):
        """Save catalog to file"""
        if self.model.filename:
            self.model.save()
            self.__set_title(filepath=self.model.filename)
        else:
            self.__save_as()
        pass
        
    def __save_as(self):
        """Save database to file under different filename."""
        path = Dialogs.ChooseDBFilename().show_dialog()
        if path:
            ret, err = self.model.save(path)
            if ret:
                self.model.config.add_recent(path)
                self.__set_title(filepath=path)
            else:
                Dialogs.Err("Error writing file - pyGTKtalog","Cannot write \
                            file %s." % path, "%s" % err)
        
    def __add_cd(self, label=None, current_id=None):
        """Add directory structure from cd/dvd disc"""
        mount = deviceHelper.volmount(self.model.config.confd['cd'])
        if mount == 'ok':
            guessed_label = deviceHelper.volname(self.model.config.confd['cd'])
            if not label:
                label = Dialogs.InputDiskLabel(guessed_label).run()
            if label != None:
                self.scan_cd = True
                for widget in self.widgets_all:
                    self.view[widget].set_sensitive(False)
                self.model.source = self.model.CD
                self.model.scan(self.model.config.confd['cd'], label,
                                current_id)
                self.model.unsaved_project = True
                self.__set_title(filepath=self.model.filename, modified=True)
            return True
        else:
            Dialogs.Wrn("Error mounting device - pyGTKtalog",
                        "Cannot mount device pointed to %s" %
                        self.model.config.confd['cd'],
                        "Last mount message:\n%s" % mount)
            return False
    
    def __add_directory(self, path=None, label=None, current_id=None):
        if not label or not path:
            res = Dialogs.PointDirectoryToAdd().run()
            if res !=(None,None):
                path = res[1]
                label = res[0]
            else:
                return False
        
        self.scan_cd = False
        self.model.source = self.model.DR
        self.model.scan(path, label, current_id)
        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        return True
        
    def __do_quit(self):
        """Quit and save window parameters to config file"""
        # check if any unsaved project is on go.
        if self.model.unsaved_project and \
            self.model.config.confd['confirmquit']:
            if not Dialogs.Qst('Quit application - pyGTKtalog',
                               'Do you really want to quit?',
                               "Current database is not saved, any changes will be lost.").run():
                return
        
        self.__store_settings()
        self.model.cleanup()
        gtk.main_quit()
        return False

    def __new_db(self):
        
        self.__tag_cloud()
        
        """Create new database file"""
        if self.model.unsaved_project:
            if not Dialogs.Qst('Unsaved data - pyGTKtalog',
                               "Current database isn't saved",
                               'All changes will be lost. Do you really want to abandon it?').run():
                return
        self.model.new()
        
        # clear "details" buffer
        buf = self.view['description'].get_buffer()
        buf.set_text("")
        self.view['description'].set_buffer(buf)
        self.view['thumb'].hide()
        
        self.__activate_ui()
        
        return
        
    def __setup_disc_treeview(self):
        """Setup TreeView discs widget as tree."""
        self.view['discs'].set_model(self.model.discs_tree)
        
        c = gtk.TreeViewColumn('Filename')
        
        # one row contains image and text
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        c.pack_start(cellpb, False)
        c.pack_start(cell, True)
        c.set_attributes(cellpb, stock_id=2)
        c.set_attributes(cell, text=1)
        
        self.view['discs'].append_column(c)
        
        # registration of treeview signals:
        
        return
        
    def __setup_iconview(self):
        """Setup IconView images widget."""
        self.view['images'].set_model(self.model.images_store)
        self.view['images'].set_pixbuf_column(1)
        return
        
    def __setup_files_treeview(self):
        """Setup TreeView files widget, as columned list."""
        self.view['files'].set_model(self.model.files_list)
        
        self.view['files'].get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        c = gtk.TreeViewColumn('Filename')
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        c.pack_start(cellpb, False)
        c.pack_start(cell, True)
        c.set_attributes(cellpb, stock_id=6)
        c.set_attributes(cell, text=1)
                
        c.set_sort_column_id(1)
        c.set_resizable(True)
        self.view['files'].append_column(c)
        
        c = gtk.TreeViewColumn('Size',gtk.CellRendererText(), text=2)
        c.set_sort_column_id(2)
        c.set_resizable(True)
        self.view['files'].append_column(c)
        
        c = gtk.TreeViewColumn('Date',gtk.CellRendererText(), text=3)
        c.set_sort_column_id(3)
        c.set_resizable(True)
        self.view['files'].append_column(c)
        return
        
    def __setup_exif_treeview(self):
        self.view['exif_tree'].set_model(self.model.exif_list)
        
        c = gtk.TreeViewColumn('EXIF key',gtk.CellRendererText(), text=0)
        c.set_sort_column_id(0)
        c.set_resizable(True)
        self.view['exif_tree'].append_column(c)
        
        c = gtk.TreeViewColumn('EXIF value',gtk.CellRendererText(), text=1)
        c.set_sort_column_id(1)
        c.set_resizable(True)
        self.view['exif_tree'].append_column(c)
        return
        
    def __abort(self):
        """When scanning thread is runing and user push the cancel button,
        models abort attribute trigger cancelation for scan operation"""
        self.model.abort = True
        return
    
    def __activate_ui(self, name=None):
        """Make UI active, and set title"""
        self.model.unsaved_project = False
        self.__set_title(filepath=name)
        for widget in self.widgets:
            try:
                self.view[widget].set_sensitive(True)
            except:
                pass
        # PyGTK FAQ entry 23.20
        while gtk.events_pending():
            gtk.main_iteration()
        return
        
    def __set_title(self, filepath=None, modified=False):
        """Set main window title"""
        if modified:
            mod = " *"
        else:
            mod = ""
            
        if filepath:
            self.view['main'].set_title("%s - pyGTKtalog%s" %
                                        (os.path.basename(filepath), mod))
        else:
            self.view['main'].set_title("untitled - pyGTKtalog%s" % mod)
        return
        
    def __store_settings(self):
        """Store window size and pane position in config file (using config
       object from model)"""
        if self.model.config.confd['savewin']:
            self.model.config.confd['wx'], self.model.config.confd['wy'] = \
            self.view['main'].get_size()
        if self.model.config.confd['savepan']:
            self.model.config.confd['h'] = self.view['hpaned1'].get_position()
            self.model.config.confd['v'] = self.view['vpaned1'].get_position()
        self.model.config.save()
        return
        
    def __popup_menu(self, event, menu='discs_popup'):
        self.view[menu].popup(None, None, None, event.button,
                                       event.time)
        self.view[menu].show_all()
        return
        
    def __generate_recent_menu(self):
        self.recent_menu = gtk.Menu()
        for i in self.model.config.recent:
            name = os.path.basename(i)
            item = gtk.MenuItem("%s" % name)
            item.connect_object("activate", self.recent_item_response, i)
            self.recent_menu.append(item)
            item.show()
        self.view['recent_files1'].set_submenu(self.recent_menu)
        return
        
    def __get_item_info(self, item):
        self.view['description'].show()
        set = self.model.get_file_info(item)
        buf = self.view['description'].get_buffer()
        
        if set.has_key('file_info'):
            buf.set_text(set['file_info'])
            if set.has_key('description'):
                tag = buf.create_tag()
                tag.set_property('weight', pango.WEIGHT_BOLD)
                buf.insert_with_tags(buf.get_end_iter(), "\nDetails:\n", tag)
                buf.insert(buf.get_end_iter(), set['description'])
        else:
            buf.set_text('')
        
        self.view['description'].set_buffer(buf)
        
        if set.has_key('images'):
            self.__setup_iconview()
            self.view['img_container'].show()
        else:
            self.view['img_container'].hide()
        
        if set.has_key('exif'):
            self.view['exif_tree'].set_model(self.model.exif_list)
            self.view['exifinfo'].show()
        else:
            self.view['exifinfo'].hide()
            
        if set.has_key('thumbnail'):
            self.view['thumb'].set_from_file(set['thumbnail'])
            self.view['thumb'].show()
        else:
            self.view['thumb'].hide()
        return
        
    def __tag_cloud(self):
        """generate tag cloud"""
        # TODO: checkit!
        def tag_cloud_click(tag, textview, event, iter, e):
            """react on click on connected tag items"""
            if event.type == gtk.gdk.BUTTON_RELEASE:
                print tag.get_property('name')
            elif event.type == gtk.gdk.MOTION_NOTIFY:
                w = \
                self.view['tag_cloud_textview'].get_window(gtk.TEXT_WINDOW_TEXT)
                if w:
                    w.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
            else:
                w = \
                self.view['tag_cloud_textview'].get_window(gtk.TEXT_WINDOW_TEXT)
                if w:
                    w.set_cursor(None)
           
                
        def insert_blank(b, iter):
            if iter.is_end() and iter.is_start():
                return iter
            else:
                b.insert(iter, " ")
                iter = b.get_end_iter()
            return iter
            
        if len(self.model.tag_cloud) > 0:
            buff = gtk.TextBuffer()
            for cloud in self.model.tag_cloud:
                iter = insert_blank(buff, buff.get_end_iter())
                tag = buff.create_tag(cloud['id'])
                tag.set_property('size-points', cloud['size'])
                tag.set_property('foreground', cloud['color'])
                tag.connect('event', tag_cloud_click, tag)
                buff.insert_with_tags(iter, cloud['name'], tag)
            self.view['tag_cloud_textview'].set_buffer(buff)
            
    def __show_stats(self, selected_id=None):
        data = self.model.get_stats(selected_id)
        label = Dialogs.StatsDialog(data).run()
        
    pass # end of class
