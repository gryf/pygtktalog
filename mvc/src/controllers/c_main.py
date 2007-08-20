# This Python file uses the following encoding: utf-8

__version__ = "0.6"
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
    db_tmp_filename = None
    unsaved_project = False
    scan_cd = False
    widgets = (
           "discs","files","details",'save1','save_as1','cut1','copy1','paste1',
           'delete1','add_cd','add_directory1','tb_save','tb_addcd','tb_find'
        )
    def __init__(self, model):
        Controller.__init__(self, model)
        return

    def register_view(self, view):
        Controller.register_view(self, view)
        
        # deaktywuj na starcie te oto widżety
        for widget in self.widgets:
            self.view[widget].set_sensitive(False)
        
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
        
        # pokaż główne okno
        self.view['main'].show();
        return

    # Podłącz sygnały:
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
        self.__addDirectory()
        
    def on_about1_activate(self,widget):
        Dialogs.Abt("pyGTKtalog", __version__, "About", ["Roman 'gryf' Dobosz"], licence)
        return
        
    def on_preferences_activate(self,widget):
        c = ConfigController(self.model.config)
        v = ConfigView(c)
        return
        
    def on_status_bar1_activate(self,widget):
        """toggle visibility of statusbat and progress bar"""
        self.model.config.confd['showstatusbar'] = self.view['status_bar1'].get_active()
        if self.view['status_bar1'].get_active():
            self.view['statusprogress'].show()
        else:
            self.view['statusprogress'].hide()
        
    def on_toolbar1_activate(self,widget):
        """toggle visibility of toolbar bar"""
        self.model.config.confd['showtoolbar'] = self.view['toolbar1'].get_active()
        if self.view['toolbar1'].get_active():
            self.view['maintoolbar'].show()
        else:
            self.view['maintoolbar'].hide()
        
    def on_save1_activate(self,widget):
        self.save()
        
    def on_tb_save_clicked(self,widget):
        self.save()
        
    def on_save_as1_activate(self,widget):
        self.save_as()
        
    def on_tb_open_clicked(self,widget):
        self.opendb()
        
    def on_open1_activate(self,widget):
        self.opendb()
        
    def on_discs_cursor_changed(self,widget):
        self.show_files()
        
    def on_discs_row_activated(self,widget):
        self.collapse_expand_branch()
        
    def on_files_cursor_changed(self,widget):
        self.show_details()
        
    def on_files_row_activated(self,widget):
        self.change_view()
    
    # Obserwowalne właściwości
    
    
    # funkcje do obsługi formularza
    
    def storeSettings(self):
        """Store window size and pane position in config file (using config object)"""
        if self.model.config.confd['savewin']:
            self.model.config.confd['wx'], self.model.config.confd['wy'] = self.view['main'].get_size()
        if self.model.config.confd['savepan']:
            self.model.config.confd['h'],self.model.config.confd['v'] = self.view['hpaned1'].get_position(), self.view['vpaned1'].get_position()
        self.model.config.save()
        pass
        
    def __addCD(self):
        """add directory structure from cd/dvd disc"""
        self.scan_cd = True
        mount = deviceHelper.volmount(self.model.config.confd['cd'])
        if mount == 'ok':
            guessed_label = deviceHelper.volname(self.model.config.confd['cd'])
            obj = Dialogs.InputDiskLabel(guessed_label)
            label = obj.run()
            if label != None:
                self.model.scan(self.model.config.confd['cd'],label)
        else:
            Dialogs.Wrn("error mounting device - pyGTKtalog","Cannot mount device pointed to %s.\nLast mount message:\n<tt>%s</tt>" % (self.model.config.confd['cd'],mount))
        
    def save(self):
        pass
        
    def save_as(self):
        pass
        
    def opendb(self):
        pass
        
    def show_files(self):
        pass
        
    def collapse_expand_branch(self):
        pass
        
    def show_details(self):
        pass
        
    def change_view(self):
        pass
    
    #####################
    # observed properetis
    def property_statusmsg_value_change(self, model, old, new):
        if self.statusbar_id != 0:
            self.view['mainStatus'].remove(self.context_id, self.statusbar_id)
        self.statusbar_id = self.view['mainStatus'].push(self.context_id, "%s" % new)
        return
        
    def property_busy_value_change(self, model, old, new):
        if new != old:
            for w in self.widgets:
                self.view[w].set_sensitive(not new)
            if not new and self.scan_cd:
                self.scan_cd = False
                # umount/eject cd
                if self.model.config.confd['eject']:
                    msg = deviceHelper.eject_cd(self.model.config.confd['ejectapp'],self.model.config.confd['cd'])
                    if msg != 'ok':
                        Dialogs.Wrn("error ejecting device - pyGTKtalog","Cannot eject device pointed to %s.\nLast eject message:\n<tt>%s</tt>" % (self.model.config.confd['cd'],msg))
                else:
                    msg = deviceHelper.volumount(self.model.config.confd['cd'])
                    if msg != 'ok':
                        Dialogs.Wrn("error unmounting device - pyGTKtalog","Cannot unmount device pointed to %s.\nLast umount message:\n<tt>%s</tt>" % (self.model.config.confd['cd'],msg))
        return
    
    def property_progress_value_change(self, model, old, new):
        self.view['progressbar1'].set_fraction(new)
        return
        
    #########################
    # private class functions
    def __addDirectory(self):
        """add directory structure from given location"""
        res = Dialogs.PointDirectoryToAdd().run()
        if res !=(None,None):
            self.model.scan(res[1],res[0])
        return

    def __doQuit(self):
        """quit and save window parameters to config file"""
        # check if any unsaved project is on go.
        if self.model.unsaved_project and self.model.config.confd['confirmquit']:
            if not Dialogs.Qst('Quit application - pyGTKtalog','Current database is not saved\nDo you really want to quit?').run():
                return
        
        self.storeSettings()
        self.model.cleanup()
        gtk.main_quit()
        return False

    def __newDB(self):
        """Create new database file"""
        if self.model.modified:
            if not Dialogs.Qst('Unsaved data - pyGTKtalog','Current database is not saved\nDo you really want to abandon it?').run():
                return
        self.model.new()
        self.model.unsaved_project = True
        self.view['main'].set_title("untitled - pyGTKtalog")
        for widget in self.widgets:
            try:
                self.view[widget].set_sensitive(True)
            except:
                pass
        # PyGTK FAQ entry 23.20
        while gtk.events_pending():
            gtk.main_iteration()
        return
    
    pass # end of class
