# This Python file uses the following encoding: utf-8

import utils._importer
import utils.globals
from gtkmvc import Controller
from models.m_config import ConfigModel
import views.v_dialogs as Dialogs
import gtk

class MainController(Controller):
    """Kontroler głównego okna aplikacji"""
    db_tmp_filename = None
    conf = ConfigModel()
    unsaved_project = False
    def __init__(self, model):
        Controller.__init__(self, model)
        
        return

    def register_view(self, view):
        Controller.register_view(self, view)
        
        # deaktywuj na starcie te oto widżety
        widgets = (
           "discs","files","details",'save1','save_as1','cut1','copy1','paste1',
           'delete1','add_cd','add_directory1','tb_save','tb_addcd','tb_find'
        )
        for widget in widgets:
            self.view[widget].set_sensitive(False)
        
        # ustaw domyślne właściwości dla poszczególnych widżetów
        self.view['main'].set_title('pyGTKtalog');
        self.view['main'].set_icon_list(gtk.gdk.pixbuf_new_from_file("pixmaps/mainicon.png"))
        self.view['detailplace'].set_sensitive(False)
        self.view['details'].hide()
        
        # załaduj konfigurację/domyślne ustawienia i przypisz je właściwościom
        self.conf.load()
        self.view['toolbar1'].set_active(self.conf.confd['showtoolbar'])
        if self.conf.confd['showtoolbar']:
            self.view['maintoolbar'].show()
        else:
            self.view['maintoolbar'].hide()
        self.view['status_bar1'].set_active(self.conf.confd['showstatusbar'])
        if self.conf.confd['showstatusbar']:
            self.view['statusprogress'].show()
        else:
            self.view['statusprogress'].hide()
        self.view['hpaned1'].set_position(self.conf.confd['h'])
        self.view['vpaned1'].set_position(self.conf.confd['v'])
        self.view['main'].resize(self.conf.confd['wx'],self.conf.confd['wy'])
        
        # zainicjalizuj statusbar
        ContextID = self.view['mainStatus'].get_context_id('detailed res')
        StatusbarID = self.view['mainStatus'].push(ContextID, "Idle")
        
        # pokaż główne okno
        self.view['main'].show();
        return

    # Podłącz sygnały:
    def on_main_destroy_event(self, window, event):
        self.doQuit()
        return True
        
    def on_tb_quit_clicked(self,widget):
        self.doQuit()
        
    def on_quit1_activate(self,widget):
        self.doQuit()
    
    def on_new1_activate(self,widget):
        self.newDB()
        
    def on_tb_new_clicked(self,widget):
        self.newDB()
        
    def on_add_cd_activate(self,widget):
        self.addCD()
        
    def on_tb_addcd_clicked(self,widget):
        self.addCD()
        
    def on_add_directory1_activate(self,widget):
        self.addDirectory()
        
    def on_about1_activate(self,widget):
        self.about()
        
    def on_properties1_activate(self,widget):
        self.preferences()
        
    def on_status_bar1_activate(self,widget):
        self.toggle_status_bar()
        
    def on_toolbar1_activate(self,widget):
        self.toggle_toolbar()
        
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
    def doQuit(self):
        """quit and save window parameters to config file"""
        #{{{
        # check if any unsaved project is on go.
        if self.unsaved_project:
            if self.conf.confd['confirmquit']:
                obj = Dialogs.Qst('Quit application - pyGTKtalog','There is not saved database\nDo you really want to quit?')
                if not obj.run():
                    return
        
        self.storeSettings()
        gtk.main_quit()
        try:
            os.unlink(self.db_tmp_filename)
        except:
            pass
        return False
    
    def storeSettings(self):
        """Store window size and pane position in config file (using config object)"""
        if self.conf.confd['savewin']:
            self.conf.confd['wx'], self.conf.confd['wy'] = self.view['main'].get_size()
        if self.conf.confd['savepan']:
            self.conf.confd['h'],self.conf.confd['v'] = self.view['hpaned1'].get_position(), self.view['vpaned1'].get_position()
        self.conf.save()
        pass
        
    def newDB(self):
        pass
        
    def addCD(self):
        pass
        
    def addDirectory(self):
        pass
        
    def toggle_toolbar(self):
        pass
        
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
    
    pass # end of class
