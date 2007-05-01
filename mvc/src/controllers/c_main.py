# This Python file uses the following encoding: utf-8

import utils._importer
import utils.globals
from gtkmvc import Controller
import gtk

class MainController(Controller):
    """Kontroler głównego okna aplikacji"""
    def __init__(self, model):
        Controller.__init__(self, model)
        return

    def register_view(self, view):
        Controller.register_view(self, view)

        # ustaw domyślne wartości dla poszczególnych widżetów
        self.view['main'].set_title('pyGTKtalog');
        self.view['main'].set_icon_list(gtk.gdk.pixbuf_new_from_file("pixmaps/mainicon.png"))
        
        # pokaż główne okno
        self.view['main'].show();
        return

    # Podłącz sygnały:
    def on_main_destroy_event(self, window, event):
        gtk.main_quit()
        return True
        
    def on_tb_quit_clicked(self,toolbutton):
        gtk.main_quit()
        
    def on_quit1_activate(self,button):
        gtk.main_quit()
        
    # Obserwowalne właściwości
    
    pass # end of class
