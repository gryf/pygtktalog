"""
    Project: pyGTKtalog
    Description: Controller for Discs TreeView
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-30
"""
import gtk

from gtkmvc import Controller

from pygtktalog.dialogs import info


class DiscsController(Controller):
    """
    Controller for discs TreeView
    """
    def __init__(self, model, view):
        """Initialize controller"""
        Controller.__init__(self, model, view)

    def register_view(self, view):
        """Default view registration stuff"""
        self.view['discs'].set_model(self.model.discs)

        col = gtk.TreeViewColumn('kolumna')

        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()

        col.pack_start(cellpb, False)
        col.pack_start(cell, True)

        col.set_attributes(cellpb, stock_id=0)
        col.set_attributes(cell, text=1)

        self.view['discs'].append_column(col)
        self.view['discs'].show()

    # signals
    def on_discs_button_press_event(self, treeview, event):
        """
        Handle right click on discs treeview. Show popup menu.
        """

        time = event.time
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
            # setup menu
            ids = self.__get_tv_selection_ids(treeview)
            for menu_item in ['update1','rename1','delete2', 'statistics1']:
                self.view.popup_menu[menu_item].set_sensitive(not not ids)

            # checkout, if we dealing with disc or directory
            # if ancestor is 'root', then activate "update" menu item
            treeiter = self.model.discs.get_iter(path)
            #ancestor = self.model.discs.get_value(treeiter, 3) == 1
            #self.view['update1'].set_sensitive(ancestor)

            self.view.popup_menu['discs_popup'].popup(None, None, None, event.button, time)

    def on_discs_cursor_changed(self, widget):
        """Show files on right treeview, after clicking the left disc
        treeview."""
        model = self.view['discs'].get_model()
        path, column = self.view['discs'].get_cursor()
        if path:
            iter = self.model.discs.get_iter(path)
            id = self.model.discs.get_value(iter, 0)
            # self.__set_files_hiden_columns_visible(False) # TODO: ale o so chozi???
            self.model.get_root_entries(id)

        return

    def on_discs_key_release_event(self, treeview, event):
        if gtk.gdk.keyval_name(event.keyval) == 'Menu':
            ids = self.__get_tv_selection_ids(treeview)
            menu_items = ['update1','rename1','delete2', 'statistics1']
            for menu_item in menu_items:
                self.view[menu_item].set_sensitive(not not ids)
            self.__popup_menu(event, 'discs_popup')
            return True
        return False

    def on_discs_row_activated(self, treeview, path, treecolumn):
        """If possible, expand or collapse branch of discs tree"""
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path, False)
        return


    # private class functions
    def __set_files_hiden_columns_visible(self, boolean):
        """switch visibility of default hidden columns in files treeview"""
        info("switch visibility of default hidden columns in files treeview")
        #self.view['files'].get_column(0).set_visible(boolean)
        #self.view['files'].get_column(2).set_visible(boolean)

    def __get_tv_selection_ids(self, treeview):
        """get selection from treeview and return coresponding ids' from
        connected model or None"""
        ids = []
        try:
            selection = treeview.get_selection()
            model, list_of_paths = selection.get_selected_rows()
            for path in list_of_paths:
                ids.append(model.get_value(model.get_iter(path), 0))
            return ids
        except:
            # DEBUG: treeview have no selection or smth is broken
            if __debug__:
                print "c_main.py: __get_tv_selection_ids(): error on",
                print "getting selected items"
            return
        return None

    def __popup_menu(self, event, menu='discs_popup'):
        """Popoup desired menu"""
        self.view.discs_popup['discs_popup'].popup(None, None, None, 0, 0)
        #self.view[menu].popup(None, None, None, event.button,
        #                               event.time)
        self.view.discs_popup['discs_popup'].show_all()
        return
