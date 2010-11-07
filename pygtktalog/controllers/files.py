"""
    Project: pyGTKtalog
    Description: Controller for Files TreeView
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-30
"""
import gtk

from gtkmvc import Controller

from pygtktalog.pygtkutils import get_tv_item_under_cursor
from pygtktalog.logger import get_logger

LOG = get_logger("files ctrl")


class FilesController(Controller):
    """
    Controller for files TreeView list.
    """

    def __init__(self, model, view):
        """
        FilesController initialization
        """
        Controller.__init__(self, model, view)
        self.DND_TARGETS = [('files_tags', 0, 69)]


    def register_view(self, view):
        """
        Register view, and setup columns for files treeview
        """
        view['files'].set_model(self.model.files)

        sigs = {"add_tag": ("activate", self.on_add_tag1_activate),
                "delete_tag": ("activate", self.on_delete_tag_activate),
                "add_thumb": ("activate", self.on_add_thumb1_activate),
                "remove_thumb": ("activate", self.on_remove_thumb1_activate),
                "add_image": ("activate", self.on_add_image1_activate),
                "remove_image": ("activate", self.on_remove_image1_activate),
                "edit": ("activate", self.on_edit2_activate),
                "delete": ("activate", self.on_delete3_activate),
                "rename": ("activate", self.on_rename2_activate)}
        for signal in sigs:
            view.menu[signal].connect(sigs[signal][0], sigs[signal][1])


        view['files'].get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        col = gtk.TreeViewColumn(_('Disc'), gtk.CellRendererText(), text=1)
        col.set_sort_column_id(1)
        col.set_resizable(True)
        col.set_visible(False)
        view['files'].append_column(col)

        col = gtk.TreeViewColumn(_('Filename'))
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        col.pack_start(cellpb, False)
        col.pack_start(cell, True)
        col.set_attributes(cellpb, stock_id=7)
        col.set_attributes(cell, text=2)
        col.set_sort_column_id(2)
        col.set_resizable(True)
        self.view['files'].append_column(col)

        col = gtk.TreeViewColumn(_('Path'), gtk.CellRendererText(), text=3)
        col.set_sort_column_id(3)
        col.set_resizable(True)
        col.set_visible(False)
        self.view['files'].append_column(col)

        col = gtk.TreeViewColumn(_('Size'), gtk.CellRendererText(), text=4)
        col.set_sort_column_id(4)
        col.set_resizable(True)
        self.view['files'].append_column(col)

        col = gtk.TreeViewColumn(_('Date'), gtk.CellRendererText(), text=5)
        col.set_sort_column_id(5)
        col.set_resizable(True)
        self.view['files'].append_column(col)
        self.view['files'].set_search_column(2)

        # setup d'n'd support
        self.view['files'].drag_source_set(gtk.gdk.BUTTON1_MASK,
                                           self.DND_TARGETS,
                                           gtk.gdk.ACTION_COPY)

    # signals
    def on_files_drag_data_get(self, treeview, context, selection,
                               targetType, eventTime):
        """responce to "data get" DnD signal"""
        # get selection, and send it to the client
        if targetType == self.DND_TARGETS[0][2]:
            # get selection
            treesrl = treeview.get_selection()
            model, list_of_paths = treesrl.get_selected_rows()
            ids = []
            for path in list_of_paths:
                fid = model.get_value(model.get_iter(path), 0)
                ids.append(fid)
            string = str(tuple(ids)).replace(",)", ")")
            selection.set(selection.target, 8, string)

    def on_files_button_press_event(self, treeview, event):
        """
        Handle right click on files treeview - show popup menu.
        """
        LOG.debug(self.on_files_button_press_event.__doc__.strip())
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))

        if event.button == 3: # Right mouse button. Show context menu.
            if pathinfo:
                path = pathinfo[0]

                # Make sure, that there is selected row
                sel = treeview.get_selection()
                sel.unselect_all()
                sel.select_path(path)

                self._popup_menu(sel, event, event.button)
            else:
                self._popup_menu(None, event, event.button)
            return True
            #try:
            #    selection = tree.get_selection()
            #    model, list_of_paths = selection.get_selected_rows()
            #except TypeError:
            #    list_of_paths = []

            #if len(list_of_paths) == 0:
            #    # try to select item under cursor
            #    try:
            #        path, column, x, y = tree.get_path_at_pos(int(event.x),
            #                                                  int(event.y))
            #    except TypeError:
            #        # failed, do not show any popup and return
            #        tree.get_selection().unselect_all()
            #        return False
            #    selection.select_path(path[0])

            #if len(list_of_paths) > 1:
            #    self.view['add_image'].set_sensitive(False)
            #    self.view['rename'].set_sensitive(False)
            #    self.view['edit'].set_sensitive(False)
            #else:
            #    self.view['add_image'].set_sensitive(True)
            #    self.view['rename'].set_sensitive(True)
            #    self.view['edit'].set_sensitive(True)
            #self.__popup_menu(event, 'files_popup')
            #return True

    def on_files_cursor_changed(self, treeview):
        """Show details of selected file/directory"""
        file_id = get_tv_item_under_cursor(treeview)
        LOG.debug("found item: %s" % file_id)
        return

    def on_files_key_release_event(self, treeview, event):
        """do something with pressed keys"""
        if gtk.gdk.keyval_name(event.keyval) == 'Menu':
            try:
                selection = treeview.get_selection()
                model, list_of_paths = selection.get_selected_rows()
                if not list_of_paths:
                    return
            except TypeError:
                return
            self._popup_menu(selection, event, 0)

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
                    f_model = treeview.get_model()
                    first_iter = f_model.get_iter_first()
                    first_child_value = f_model.get_value(first_iter, 0)
                    # get two steps up
                    val = self.model.get_parent_id(first_child_value)
                    parent_value = self.model.get_parent_id(val)
                    iter = self.model.discs_tree.get_iter_first()
                    while iter:
                        current_value = self.model.discs_tree.get_value(iter,
                                                                        0)
                        if current_value == parent_value:
                            path = self.model.discs_tree.get_path(iter)
                            self.view['discs'].set_cursor(path)
                            iter = None
                        else:
                            iter = self.model.discs_tree.iter_next(iter)
        #if gtk.gdk.keyval_name(event.keyval) == 'Delete':
        #    for file_id in  self.__get_tv_selection_ids(treeview):
        #        self.main.delete(file_id)

        #ids = self.__get_tv_selection_ids(self.view['files'])

    def on_files_row_activated(self, files_obj, row, column):
        """On directory doubleclick in files listview dive into desired
        branch."""
        f_iter = self.model.files_list.get_iter(row)
        current_id = self.model.files_list.get_value(f_iter, 0)

        if self.model.files_list.get_value(f_iter, 6) == 1:
            # ONLY directories. files are omitted.
            self.__set_files_hiden_columns_visible(False)
            self.model.get_root_entries(current_id)

            d_path, d_column = self.view['discs'].get_cursor()
            if d_path:
                if not self.view['discs'].row_expanded(d_path):
                    self.view['discs'].expand_row(d_path, False)

                discs_model = self.model.discs_tree
                iterator = discs_model.get_iter(d_path)
                new_iter = discs_model.iter_children(iterator)
                if new_iter:
                    while new_iter:
                        current_value = discs_model.get_value(new_iter, 0)
                        if current_value == current_id:
                            path = discs_model.get_path(new_iter)
                            self.view['discs'].set_cursor(path)
                        new_iter = discs_model.iter_next(new_iter)
        return

    def on_add_tag1_activate(self, menu_item): pass
    def on_delete_tag_activate(self, menuitem): pass
    def on_add_thumb1_activate(self, menuitem): pass
    def on_remove_thumb1_activate(self, menuitem): pass
    def on_add_image1_activate(self, menuitem): pass
    def on_remove_image1_activate(self, menuitem): pass
    def on_edit2_activate(self, menuitem): pass
    def on_delete3_activate(self, menuitem): pass
    def on_rename2_activate(self, menuitem): pass

    # private methods
    def _popup_menu(self, selection, event, button):
        """
        Popup menu for files treeview. Gather information from discs model,
        and trigger menu popup.
        """
        LOG.debug(self._popup_menu.__doc__.strip())
        if selection is None:
            self.view.menu.set_menu_items_sensitivity(False)
        else:
            model, list_of_paths = selection.get_selected_rows()

            for path in list_of_paths:
                self.view.menu.set_menu_items_sensitivity(True)

        self.view.menu['files_popup'].popup(None, None, None,
                                            button, event.time)

