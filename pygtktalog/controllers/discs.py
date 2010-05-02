"""
    Project: pyGTKtalog
    Description: Controller for Discs TreeView
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-30
"""
import gtk

from gtkmvc import Controller

from pygtktalog.logger import get_logger

LOG = get_logger("discs ctrl")


class DiscsController(Controller):
    """
    Controller for discs TreeView
    """
    def __init__(self, model, view):
        """Initialize controller"""
        Controller.__init__(self, model, view)

    def register_view(self, view):
        """
        Do DiscTree registration
        """
        view['discs'].set_model(self.model.discs)

        # connect signals to popup menu - framework somehow omits automatic
        # signal connection for subviews which are not under included to
        # widgets tree
        sigs = {'expand_all': ('activate', self.on_expand_all_activate),
                'collapse_all': ('activate', self.on_collapse_all_activate),
                'update': ('activate', self.on_update_activate),
                'rename': ('activate', self.on_rename_activate),
                'delete': ('activate', self.on_delete_activate),
                'statistics': ('activate', self.on_statistics_activate)}
        for signal in sigs:
            view.menu[signal].connect(sigs[signal][0], sigs[signal][1])

        col = gtk.TreeViewColumn('kolumna')

        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()

        col.pack_start(cellpb, False)
        col.pack_start(cell, True)

        col.set_attributes(cellpb, stock_id=0)
        col.set_attributes(cell, text=1)

        view['discs'].append_column(col)
        view['discs'].show()



    # signals
    def on_discs_button_press_event(self, treeview, event):
        """
        Handle right click on discs treeview - show popup menu.
        """
        LOG.debug('on_discs_button_press_event')
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))

        if event.button == 3 and pathinfo:
            path = pathinfo[0]

            # Make sure, that there is selected row
            sel = treeview.get_selection()
            sel.unselect_all()
            sel.select_path(path)

            self._popup_menu(sel, event, event.button)
            return True

    def on_discs_cursor_changed(self, widget):
        """
        Show files on right treeview, after clicking the left disc treeview.
        """
        LOG.debug('on_discs_cursor_changed')

    def on_discs_key_release_event(self, treeview, event):
        """
        Trigger popup menu by pressing 'menu' key
        """
        LOG.debug('on_discs_key_release_event')
        if gtk.gdk.keyval_name(event.keyval) == 'Menu':
            self._popup_menu(treeview.get_selection(), event, 0)
            return True
        return False

    def on_discs_row_activated(self, treeview, path, treecolumn):
        """
        If possible, expand or collapse branch of discs tree
        """
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path, False)

    def on_expand_all_activate(self, menu_item):
        """
        Expand all
        """
        self.view['discs'].expand_all()

    def on_collapse_all_activate(self, menu_item):
        """
        Collapse all
        """
        self.view['discs'].collapse_all()

    def on_update_activate(self, menu_item):
        """
        Trigger update specified tree entry
        """
        raise NotImplementedError

    def on_rename_activate(self, menu_item):
        """
        Rename disk or directory
        """
        raise NotImplementedError

    def on_delete_activate(self, menu_item):
        """
        Delete disk or directory from catalog
        """
        raise NotImplementedError

    def on_statistics_activate(self, menu_item):
        """
        Show statistics for selected item
        """
        raise NotImplementedError

    def _popup_menu(self, selection, event, button):
        """
        Popup menu for discs treeview. Gather information from discs model,
        and trigger menu popup.
        """
        LOG.debug('_popup_menu')
        model, list_of_paths = selection.get_selected_rows()

        for path in list_of_paths:
            self.view.menu.set_update_sensitivity(not model.get_value(\
                    model.get_iter(path), 4).parent_id == 1)

        self.view.menu['discs_popup'].popup(None, None, None,
                                            button, event.time)
