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
        self.files_model = self.model.files

    def register_view(self, view):
        """
        Register view, and setup columns for files treeview
        """
        view['files'].set_model(self.files_model.files)

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
        LOG.debug("Mouse button pressed")
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))

        if event.button == 3:  # Right mouse button. Show context menu.
            LOG.debug("It's a right button")
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
        LOG.debug("It's other button")

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
            row, gtk_column = self.view['files'].get_cursor()
            if row and gtk_column:
                fileob = self.files_model.get_value(row)
                if fileob.parent.parent.id != 1:
                    self.files_model.refresh(fileob.parent.parent)
                    # TODO: synchronize with disks
                    self.model.discs.currentdir = fileob.parent.parent

            self.view['files'].grab_focus()


    def on_files_row_activated(self, files_obj, row, column):
        """
        On directory doubleclick in files listview dive into desired branch.
        """

        fileob = self.files_model.get_value(row=row)
        if not fileob.children:
            # ONLY directories. files are omitted.
            return

        self.files_model.refresh(fileob)
        self.model.discs.currentdir = fileob
        self.view['files'].grab_focus()

        # TODO: synchronize with disks
        return

    def on_add_tag1_activate(self, menu_item):
        """
        TODO
        """
        LOG.debug(self.on_add_tag1_activate.__doc__.strip())
        raise NotImplementedError

    def on_delete_tag_activate(self, menuitem):
        """
        TODO
        """
        LOG.debug(self.on_delete_tag_activate.__doc__.strip())
        raise NotImplementedError

    def on_add_thumb1_activate(self, menuitem):
        """
        TODO
        """
        LOG.debug(self.on_add_thumb1_activate.__doc__.strip())
        raise NotImplementedError

    def on_remove_thumb1_activate(self, menuitem):
        """
        TODO
        """
        LOG.debug(self.on_remove_thumb1_activate.__doc__.strip())
        raise NotImplementedError

    def on_add_image1_activate(self, menuitem):
        """
        TODO
        """
        LOG.debug(self.on_add_image1_activate.__doc__.strip())
        raise NotImplementedError

    def on_remove_image1_activate(self, menuitem):
        """
        TODO
        """
        LOG.debug(self.on_remove_image1_activate.__doc__.strip())
        raise NotImplementedError

    def on_edit2_activate(self, menuitem):
        """
        TODO
        """
        LOG.debug(self.on_edit2_activate.__doc__.strip())
        raise NotImplementedError

    def on_delete3_activate(self, menuitem):
        """
        TODO
        """
        LOG.debug(self.on_delete3_activate.__doc__.strip())
        raise NotImplementedError

    def on_rename2_activate(self, menuitem):
        """
        TODO
        """
        LOG.debug(self.on_rename2_activate.__doc__.strip())
        raise NotImplementedError

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
