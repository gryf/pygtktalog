# This Python file uses the following encoding: utf-8

__version__ = "0.7"
licence = \
"""
GPL v2
http://www.gnu.org/licenses/gpl.txt
"""

import utils._importer
import utils.globals
from utils import deviceHelper
from gtkmvc import Controller

from c_config import ConfigController
from views.v_config import ConfigView
from models.m_config import ConfigModel

import views.v_dialogs as Dialogs

import gtk

import datetime

class MainController(Controller):
    """Kontroler głównego okna aplikacji"""
    scan_cd = False
    widgets = (
           "discs","files","details",
           'save1','save_as1','cut1','copy1','paste1','delete1','add_cd','add_directory1',
           'tb_save','tb_addcd','tb_find',
        )
    widgets_all = (
           "discs","files","details",
           'file1','edit1','add_cd','add_directory1','help1',
           'tb_save','tb_addcd','tb_find','tb_new','tb_open','tb_quit',
        )
    widgets_cancel = ('cancel','cancel1')
    
    def __init__(self, model):
        """Initialize controller"""
        Controller.__init__(self, model)
        return

    def register_view(self, view):
        Controller.register_view(self, view)
        
        # deaktywuj na starcie te oto widżety
        for widget in self.widgets:
            self.view[widget].set_sensitive(False)
        # dodatkowo deaktywuj knefle 'cancel'
        for widget in self.widgets_cancel:
            self.view[widget].set_sensitive(False)
            
        # ukryj przycisk "debug", jeśli nie debugujemy.
        if __debug__:
            self.view['debugbtn'].show()
        else:
            self.view['debugbtn'].hide()
        
        # ustaw domyślne właściwości dla poszczególnych widżetów
        self.view['main'].set_title('pyGTKtalog');
        self.view['main'].set_icon_list(gtk.gdk.pixbuf_new_from_file("pixmaps/mainicon.png"))
        self.view['detailplace'].set_sensitive(False)
        self.view['details'].hide()
        
        # załaduj konfigurację/domyślne ustawienia i przypisz je właściwościom
        
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
        
    def on_add_directory1_activate(self,widget):
        """Show dialog for choose drectory to add from filesystem."""
        res = Dialogs.PointDirectoryToAdd().run()
        if res !=(None,None):
            self.model.scan(res[1],res[0])
        return
        
    def on_about1_activate(self,widget):
        """Show about dialog"""
        Dialogs.Abt("pyGTKtalog", __version__, "About", ["Roman 'gryf' Dobosz"], licence)
        return
        
    def on_preferences_activate(self,widget):
        c = ConfigController(self.model.config)
        v = ConfigView(c)
        return
        
    def on_status_bar1_activate(self,widget):
        """Toggle visibility of statusbat and progress bar."""
        self.model.config.confd['showstatusbar'] = self.view['status_bar1'].get_active()
        if self.view['status_bar1'].get_active():
            self.view['statusprogress'].show()
        else:
            self.view['statusprogress'].hide()
        
    def on_toolbar1_activate(self,widget):
        """Toggle visibility of toolbar bar."""
        self.model.config.confd['showtoolbar'] = self.view['toolbar1'].get_active()
        if self.view['toolbar1'].get_active():
            self.view['maintoolbar'].show()
        else:
            self.view['maintoolbar'].hide()
        
    def on_save1_activate(self,widget):
        self.__save()
        
    def on_tb_save_clicked(self,widget):
        self.__save()
        
    def on_save_as1_activate(self,widget):
        self.__save_as()
        
    def on_tb_open_clicked(self,widget):
        self.__open()
        
    def on_open1_activate(self,widget):
        self.__open()
        
    def on_discs_cursor_changed(self,widget):
        """Show files on right treeview, after clicking the left disc treeview."""
        model = self.view['discs'].get_model()
        selected_item = self.model.discsTree.get_value(self.model.discsTree.get_iter(self.view['discs'].get_cursor()[0]),0)
        if __debug__:
            print "on_discs_cursor_changed ",selected_item
        self.model.get_root_entries(selected_item)
        
        self.view['details'].show()
        txt = self.model.get_file_info(selected_item)
        buf = self.view['details'].get_buffer()
        buf.set_text(txt)
        self.view['details'].set_buffer(buf)
        return
        
    def on_discs_row_activated(self, treeview, path, treecolumn):
        """If possible, expand or collapse branch of discs tree"""
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path,False)
        
    def on_files_cursor_changed(self,treeview):
        """Show details of selected file"""
        model, paths = treeview.get_selection().get_selected_rows()
        try:
            itera = model.get_iter(paths[0])
            if model.get_value(itera,4) == 1:
                #directory, do nothin', just turn off view
                self.view['details'].hide()
                buf = self.view['details'].get_buffer()
                buf.set_text('')
                self.view['details'].set_buffer(buf)
                if __debug__:
                    print "on_files_cursor_changed: directory selected"
            else:
                #file, show what you got.
                self.view['details'].show()
                selected_item = self.model.filesList.get_value(model.get_iter(treeview.get_cursor()[0]),0)
                txt = self.model.get_file_info(selected_item)
                
                buf = self.view['details'].get_buffer()
                buf.set_text(txt)
                self.view['details'].set_buffer(buf)
                if __debug__:
                    print "on_files_cursor_changed: some other thing selected"
        except:
            if __debug__:
                print "on_files_cursor_changed: insufficient iterator"
        return
        
    def on_files_row_activated(self, files_obj, row, column):
        """On directory doubleclick in files listview dive into desired branch."""
        # TODO: można by też podczepić klawisz backspace do przechodzenia poziom wyżej.
        f_iter = self.model.filesList.get_iter(row)
        current_id = self.model.filesList.get_value(f_iter,0)
        
        if self.model.filesList.get_value(f_iter,4) == 1:
            # ONLY directories. files are omitted.
            self.model.get_root_entries(current_id)
            
            d_path, d_column = self.view['discs'].get_cursor()
            if d_path!=None:
                if not self.view['discs'].row_expanded(d_path):
                    self.view['discs'].expand_row(d_path,False)
            
            new_iter = self.model.discsTree.iter_children(self.model.discsTree.get_iter(d_path))
            if new_iter:
                while new_iter:
                    if self.model.discsTree.get_value(new_iter,0) == current_id:
                        self.view['discs'].set_cursor(self.model.discsTree.get_path(new_iter))
                    new_iter = self.model.discsTree.iter_next(new_iter)
        return
        
    def on_cancel1_activate(self,widget):
        self.__abort()
        
    def on_cancel_clicked(self,widget):
        self.__abort()
        
    def on_tb_find_clicked(self,widget):
        # TODO: zaimplementować wyszukiwarkę
        return
        
    def on_debugbtn_clicked(self,widget):
        """Debug, do usunięcia w wersji stable, włącznie z kneflem w GUI"""
        if __debug__:
            print "\ndebug:"
            print "------"
            print "unsaved_project = %s" % self.model.unsaved_project
            print "filename = %s" % self.model.filename
            print "internal_filename = %s" % self.model.internal_filename
            print "db_connection = %s" % self.model.db_connection
            print "abort = %s" % self.model.abort
            
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
                if self.model.config.confd['eject']:
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
    def __open(self):
        """Open catalog file"""
        if self.model.unsaved_project and self.model.config.confd['confirmabandon']:
            obj = dialogs.Qst('Unsaved data - pyGTKtalog','There is not saved database','Pressing "Ok" will abandon catalog.')
            if not obj.run():
                return
        path = Dialogs.LoadDBFile().run()
        if path:
            if not self.model.open(path):
                Dialogs.Err("Error opening file - pyGTKtalog","Cannot open file %s." % self.opened_catalog)
            else:
                self.__activateUI(path)
    
    def __save(self):
        """Save catalog to file"""
        #{{{
        if self.model.filename:
            self.model.save()
        else:
            self.__save_as()
        pass
        
    def __save_as(self):
        """Save database to file under different filename."""
        path = Dialogs.ChooseDBFilename().show_dialog()
        if path:
            self.view['main'].set_title("%s - pyGTKtalog" % path)
            self.model.save(path)
        pass
        
    def __addCD(self):
        """Add directory structure from cd/dvd disc"""
        mount = deviceHelper.volmount(self.model.config.confd['cd'])
        if mount == 'ok':
            guessed_label = deviceHelper.volname(self.model.config.confd['cd'])
            label = Dialogs.InputDiskLabel(guessed_label).run()
            if label != None:
                self.scan_cd = True
                for widget in self.widgets_all:
                    self.view[widget].set_sensitive(False)
                self.model.scan(self.model.config.confd['cd'],label)
        else:
            Dialogs.Wrn("Error mounting device - pyGTKtalog",
                        "Cannot mount device pointed to %s" % self.model.config.confd['cd'],
                        "Last mount message:\n%s" % mount)
        
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
        txt = ""
        buf = self.view['details'].get_buffer()
        buf.set_text(txt)
        self.view['details'].set_buffer(buf)
        
        self.__activateUI()
        
        return
        
    def __setup_disc_treeview(self):
        """Setup TreeView discs widget as tree."""
        self.view['discs'].set_model(self.model.discsTree)
        
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
        self.view['files'].set_model(self.model.filesList)
        
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
    
    def __activateUI(self, name='untitled'):
        """Make UI active, and set title"""
        self.model.unsaved_project = False
        self.view['main'].set_title("%s - pyGTKtalog" % name)
        for widget in self.widgets:
            try:
                self.view[widget].set_sensitive(True)
            except:
                pass
        # PyGTK FAQ entry 23.20
        while gtk.events_pending():
            gtk.main_iteration()
        return
    
    def __storeSettings(self):
        """Store window size and pane position in config file (using config object from model)"""
        if self.model.config.confd['savewin']:
            self.model.config.confd['wx'], self.model.config.confd['wy'] = self.view['main'].get_size()
        if self.model.config.confd['savepan']:
            self.model.config.confd['h'],self.model.config.confd['v'] = self.view['hpaned1'].get_position(), self.view['vpaned1'].get_position()
        self.model.config.save()
        pass
    
    pass # end of class
