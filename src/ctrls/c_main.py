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
from c_details import DetailsController
from views.v_config import ConfigView
from models.m_config import ConfigModel

import views.v_dialogs as Dialogs

import gtk

import datetime

class MainController(Controller):
    """Controller for main application window"""
    scan_cd = False
    widgets = (
           "discs","files",
           'save1','save_as1','cut1','copy1','paste1','delete1','add_cd','add_directory1',
           'tb_save','tb_addcd','tb_find',
        )
    widgets_all = (
           "discs","files",
           'file1','edit1','add_cd','add_directory1','help1',
           'tb_save','tb_addcd','tb_find','tb_new','tb_open','tb_quit',
        )
    widgets_cancel = ('cancel','cancel1')
    
    def __init__(self, model):
        """Initialize controller"""
        Controller.__init__(self, model)
        self.details = DetailsController(model.details)
        return

    def register_view(self, view):
        Controller.register_view(self, view)
        
        # Make widget set non active
        for widget in self.widgets:
            self.view[widget].set_sensitive(False)
        
        # Make not active "Cancel" button and menuitem
        for widget in self.widgets_cancel:
            self.view[widget].set_sensitive(False)
            
        # hide "debug" button, if production (i.e. python OT running with -OO option)
        if __debug__:
            self.view['debugbtn'].show()
        else:
            self.view['debugbtn'].hide()
        
        # ustaw domyślne właściwości dla poszczególnych widżetów
#        self.view['main'].set_icon_list(gtk.gdk.pixbuf_new_from_file("pixmaps/mainicon.png"))
        #self.view['detailplace'].set_sensitive(False)
        #self.view['exifTab'].hide()
        #self.view['animeTab'].hide()
        
        # load configuration/defaults and set it to properties
        self.view['toolbar1'].set_active(self.model.config.confd['showtoolbar'])
        if self.model.config.confd['showtoolbar']:
            self.view['maintoolbar'].show()
        else:
            self.view['maintoolbar'].hide()
        self.view['status_bar1'].set_active(self.model.config.confd['showstatusbar'])
        if self.model.config.confd['showstatusbar']:
            self.view['statusprogress'].show()
        else:
            self.view['statusprogress'].hide()
        self.view['hpaned1'].set_position(self.model.config.confd['h'])
        self.view['vpaned1'].set_position(self.model.config.confd['v'])
        self.view['main'].resize(self.model.config.confd['wx'],self.model.config.confd['wy'])
        
        # zainicjalizuj statusbar
        self.context_id = self.view['mainStatus'].get_context_id('detailed res')
        self.statusbar_id = self.view['mainStatus'].push(self.context_id, "Idle")
        
        # inicjalizacja drzew
        self.__setup_disc_treeview()
        self.__setup_files_treeview()
        
        # w przypadku podania jako argument z linii komend bazy, odblokuj cały ten staff
        if self.model.filename != None:
            self.__activateUI(self.model.filename)
        
        # register detail subview
        #self.view.create_sub_view(self.details)
        
        # generate recent menu
        self.__generate_recent_menu()
        # Show main window
        self.view['main'].show();
        return
        
    #########################################################################
    # Connect signals from GUI, like menu objects, toolbar buttons and so on.
    def on_main_destroy_event(self, window, event):
        self.__doQuit()
        return True
        
    def on_tb_quit_clicked(self,widget):
        self.__doQuit()
        
    def on_quit1_activate(self,widget):
        self.__doQuit()
    
    def on_new1_activate(self,widget):
        self.__newDB()
        
    def on_tb_new_clicked(self,widget):
        self.__newDB()
        
    def on_add_cd_activate(self,widget):
        self.__addCD()
        
    def on_tb_addcd_clicked(self,widget):
        self.__addCD()
        
    def on_add_directory1_activate(self, widget):
        """Show dialog for choose drectory to add from filesystem."""
        self.__addDirectory()
        return
        
    def on_about1_activate(self,widget):
        """Show about dialog"""
        Dialogs.Abt("pyGTKtalog", __version__, "About", ["Roman 'gryf' Dobosz"], licence)
        return
        
    def on_preferences_activate(self, widget):
        c = ConfigController(self.model.config)
        v = ConfigView(c)
        return
        
    def on_status_bar1_activate(self, widget):
        """Toggle visibility of statusbat and progress bar."""
        self.model.config.confd['showstatusbar'] = self.view['status_bar1'].get_active()
        if self.view['status_bar1'].get_active():
            self.view['statusprogress'].show()
        else:
            self.view['statusprogress'].hide()
        
    def on_toolbar1_activate(self, widget):
        """Toggle visibility of toolbar bar."""
        self.model.config.confd['showtoolbar'] = self.view['toolbar1'].get_active()
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
        
    def on_tb_open_clicked(self, widget):
        self.__open()
        
    def on_open1_activate(self, widget):
        self.__open()
        
    def on_discs_cursor_changed(self, widget):
        """Show files on right treeview, after clicking the left disc treeview."""
        model = self.view['discs'].get_model()
        selected_item = self.model.discs_tree.get_value(self.model.discs_tree.get_iter(self.view['discs'].get_cursor()[0]),0)
        if __debug__:
            print "c_main.py, on_discs_cursor_changed()",selected_item
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
    
    def on_discs_button_press_event(self, treeview, event):
        try:
            path, column, x, y = treeview.get_path_at_pos(int(event.x), int(event.y))
        except TypeError:
            treeview.get_selection().unselect_all()
            return False
                
        if event.button == 3:
            """show context menu"""
            try:
                model, list_of_paths = treeview.get_selection().get_selected_rows()
            except TypeError:
                list_of_paths = []
                pass
                
            if path not in list_of_paths:
                treeview.get_selection().unselect_all()
                treeview.get_selection().select_path(path)
            
            if self.model.discs_tree.get_value(self.model.discs_tree.get_iter(path),3) == 1:
                # if ancestor is 'root', then activate "update" menu item
                self.view['update1'].set_sensitive(True)
            else:
                self.view['update1'].set_sensitive(False)
            self.__popup_discs_menu(event)
            
        # elif event.button == 1: # Left click
            # """Show files on right treeview, after clicking the left disc treeview."""
            # model = self.view['discs'].get_model()
            # selected_item = self.model.discs_tree.get_value(self.model.discs_tree.get_iter(path),0)
            # if __debug__:
                # print "c_main.py, on_discs_cursor_changed()",selected_item
            # self.model.get_root_entries(selected_item)
            # 
            # self.view['details'].show()
            # txt = self.model.get_file_info(selected_item)
            # buf = self.view['details'].get_buffer()
            # buf.set_text(txt)
            # self.view['details'].set_buffer(buf)
            # return
            
    def on_expand_all1_activate(self, menuitem):
        self.view['discs'].expand_all()
        return
        
    def on_collapse_all1_activate(self, menuitem):
        self.view['discs'].collapse_all()
        return
        
    def on_files_cursor_changed(self,treeview):
        """Show details of selected file"""
        model, paths = treeview.get_selection().get_selected_rows()
        try:
            itera = model.get_iter(paths[0])
            if model.get_value(itera,4) == 1:
                #directory, do nothin', just turn off view
                '''self.view['details'].hide()
                buf = self.view['details'].get_buffer()
                buf.set_text('')
                self.view['details'].set_buffer(buf)'''
                if __debug__:
                    print "c_main.py: on_files_cursor_changed() directory selected"
            else:
                #file, show what you got.
                selected_item = self.model.files_list.get_value(model.get_iter(treeview.get_cursor()[0]),0)
                self.__get_item_info(selected_item)
                if __debug__:
                    print "c_main.py: on_files_cursor_changed() some other thing selected"
        except:
            if __debug__:
                print "c_main.py: on_files_cursor_changed() insufficient iterator"
        return
        
    def on_files_row_activated(self, files_obj, row, column):
        """On directory doubleclick in files listview dive into desired branch."""
        # TODO: map backspace key for moving to upper level of directiories
        f_iter = self.model.files_list.get_iter(row)
        current_id = self.model.files_list.get_value(f_iter,0)
        
        if self.model.files_list.get_value(f_iter,4) == 1:
            # ONLY directories. files are omitted.
            self.model.get_root_entries(current_id)
            
            d_path, d_column = self.view['discs'].get_cursor()
            if d_path!=None:
                if not self.view['discs'].row_expanded(d_path):
                    self.view['discs'].expand_row(d_path,False)
            
            new_iter = self.model.discs_tree.iter_children(self.model.discs_tree.get_iter(d_path))
            if new_iter:
                while new_iter:
                    if self.model.discs_tree.get_value(new_iter,0) == current_id:
                        self.view['discs'].set_cursor(self.model.discs_tree.get_path(new_iter))
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
        
    def on_update1_activate(self, menu_item):
        """Update disc under cursor position"""
        
        # determine origin label and filepath
        path = self.view['discs'].get_cursor()
        filepath, label = self.model.get_label_and_filepath(path)
        
        if self.model.get_source(path) == self.model.CD:
            if self.__addCD(label):
                self.model.delete(self.model.discs_tree.get_iter(path[0],0))
                pass
        elif self.model.get_source(path) == self.model.DR:
            if self.__addDirectory(filepath, label):
                self.model.delete(self.model.discs_tree.get_iter(path[0]))
                pass
        return
        
    def on_delete2_activate(self, menu_item):
        model = self.view['discs'].get_model()
        try:
            selected_iter = self.model.discs_tree.get_iter(self.view['discs'].get_cursor()[0])
        except:
            return
        if self.model.config.confd['delwarn']:
            name = self.model.discs_tree.get_value(selected_iter,1)
            obj = Dialogs.Qst('Delete %s' % name, 'Delete %s?' % name, 'Object will be permanently removed.')
            if not obj.run():
                return
        self.model.delete(selected_iter)
        self.model.unsaved_project = True
        self.__setTitle(filepath=self.model.filename, modified=True)
        return

    def on_debugbtn_clicked(self,widget):
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
            it = self.model.tags_list.get_iter_first()
            myit = self.model.tags_list.insert_before(None,None)
            self.model.tags_list.set_value(myit,0,0)
            self.model.tags_list.set_value(myit,1,"nazwa")
            self.model.tags_list.set_value(myit,2,231233)
            print "source: %s" % self.model.source
            
    #####################
    # observed properetis
    def property_statusmsg_value_change(self, model, old, new):
        if self.statusbar_id != 0:
            self.view['mainStatus'].remove(self.context_id, self.statusbar_id)
        self.statusbar_id = self.view['mainStatus'].push(self.context_id, "%s" % new)
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
                if self.model.config.confd['eject'] and self.model.config.confd['ejectapp']:
                    msg = deviceHelper.eject_cd(self.model.config.confd['ejectapp'],self.model.config.confd['cd'])
                    if msg != 'ok':
                        Dialogs.Wrn("error ejecting device - pyGTKtalog",
                                    "Cannot eject device pointed to %s" % self.model.config.confd['cd'],
                                    "Last eject message:\n%s" % msg)
                else:
                    msg = deviceHelper.volumount(self.model.config.confd['cd'])
                    if msg != 'ok':
                        Dialogs.Wrn("error unmounting device - pyGTKtalog",
                                    "Cannot unmount device pointed to %s" % self.model.config.confd['cd'],
                                    "Last umount message:\n%s" % msg)
        return
    
    def property_progress_value_change(self, model, old, new):
        self.view['progressbar1'].set_fraction(new)
        return
        
    #########################
    # private class functions
    def __open(self, path=None):
        """Open catalog file"""
        if self.model.unsaved_project and self.model.config.confd['confirmabandon']:
            obj = Dialogs.Qst('Unsaved data - pyGTKtalog','There is not saved database','Pressing "Ok" will abandon catalog.')
            if not obj.run():
                return
        
        if not path:
            path = Dialogs.LoadDBFile().run()
        
        if path:
            if not self.model.open(path):
                Dialogs.Err("Error opening file - pyGTKtalog","Cannot open file %s." % path)
            else:
                self.__generate_recent_menu()
                self.__activateUI(path)
        return
        
    def __save(self):
        """Save catalog to file"""
        if self.model.filename:
            self.model.save()
            self.__setTitle(filepath=self.model.filename)
        else:
            self.__save_as()
        pass
        
    def __save_as(self):
        """Save database to file under different filename."""
        path = Dialogs.ChooseDBFilename().show_dialog()
        if path:
            self.__setTitle(filepath=path)
            self.model.save(path)
            self.model.config.add_recent(path)
        pass
        
    def __addCD(self, label=None):
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
                self.model.scan(self.model.config.confd['cd'],label)
                self.model.unsaved_project = True
                self.__setTitle(filepath=self.model.filename, modified=True)
            return True
        else:
            Dialogs.Wrn("Error mounting device - pyGTKtalog",
                        "Cannot mount device pointed to %s" % self.model.config.confd['cd'],
                        "Last mount message:\n%s" % mount)
            return False
    
    def __addDirectory(self, path=None, label=None):
        if not label or not path:
            res = Dialogs.PointDirectoryToAdd().run()
            if res !=(None,None):
                path = res[1]
                label = res[0]
            else:
                return False
        
        self.scan_cd = False
        self.model.source = self.model.DR
        self.model.scan(path, label)
        self.model.unsaved_project = True
        self.__setTitle(filepath=self.model.filename, modified=True)
        return True
        
    def __doQuit(self):
        """Quit and save window parameters to config file"""
        # check if any unsaved project is on go.
        if self.model.unsaved_project and self.model.config.confd['confirmquit']:
            if not Dialogs.Qst('Quit application - pyGTKtalog',
                               'Do you really want to quit?',
                               "Current database is not saved, any changes will be lost.").run():
                return
        
        self.__storeSettings()
        self.model.cleanup()
        gtk.main_quit()
        return False

    def __newDB(self):
        """Create new database file"""
        if self.model.unsaved_project:
            if not Dialogs.Qst('Unsaved data - pyGTKtalog',
                               "Current database isn't saved",
                               'All changes will be lost. Do you really want to abandon it?').run():
                return
        self.model.new()
        
        # clear "details" buffer
        '''txt = ""
        buf = self.view['details'].get_buffer()
        buf.set_text(txt)
        self.view['details'].set_buffer(buf)'''
        
        self.__activateUI()
        
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
        
    def __setup_tags_treeview(self):
        """Setup TreeView discs widget as tree."""
        self.view['tags'].set_model(self.model.tagsTree)
        
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
        
        c = gtk.TreeViewColumn('Category',gtk.CellRendererText(), text=5)
        c.set_sort_column_id(5)
        c.set_resizable(True)
        self.view['files'].append_column(c)
        
        # registration of treeview signals:
        
        return
        
    def __abort(self):
        """When scanning thread is activated and user push the cancel button,
        models abort attribute trigger cancelation for scan operation"""
        self.model.abort = True
        return
    
    def __activateUI(self, name=False):
        """Make UI active, and set title"""
        self.model.unsaved_project = False
        self.__setTitle(filepath=name)
        for widget in self.widgets:
            try:
                self.view[widget].set_sensitive(True)
            except:
                pass
        # PyGTK FAQ entry 23.20
        while gtk.events_pending():
            gtk.main_iteration()
        return
        
    def __setTitle(self, filepath=None, modified=False):
        """Set main window title"""
        if modified:
            mod = " *"
        else:
            mod = ""
            
        if filepath:
            self.view['main'].set_title("%s - pyGTKtalog%s" % (os.path.basename(filepath), mod))
        else:
            self.view['main'].set_title("untitled - pyGTKtalog%s" % mod)
        return
        
    def __storeSettings(self):
        """Store window size and pane position in config file (using config object from model)"""
        if self.model.config.confd['savewin']:
            self.model.config.confd['wx'], self.model.config.confd['wy'] = self.view['main'].get_size()
        if self.model.config.confd['savepan']:
            self.model.config.confd['h'],self.model.config.confd['v'] = self.view['hpaned1'].get_position(), self.view['vpaned1'].get_position()
        self.model.config.save()
        return
        
    def __popup_discs_menu(self, event):
        self.view['discs_popup'].popup(None, None, None, event.button, event.time)
        self.view['discs_popup'].show_all()
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
        '''self.view['details'].show()
        txt = self.model.get_file_info(item)
        buf = self.view['details'].get_buffer()
        buf.set_text(txt)
        self.view['details'].set_buffer(buf)'''
        return
    pass # end of class
