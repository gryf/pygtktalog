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
        """
        Initialize DiscsController
        """
        LOG.debug(self.__init__.__doc__.strip())
        Controller.__init__(self, model, view)
        self.discs_model = self.model.discs.discs

    def register_view(self, view):
        """
        Do DiscTree registration
        """
        LOG.debug(self.register_view.__doc__.strip())
        view['discs'].set_model(self.discs_model)

        # register observers
        self.model.discs.register_observer(self)

        # connect signals to popup menu - framework somehow omits automatic
        # signal connection for subviews which are not included to widgets
        # tree
        sigs = {'expand_all': ('activate', self.on_expand_all_activate),
                'collapse_all': ('activate', self.on_collapse_all_activate),
                'update': ('activate', self.on_update_activate),
                'rename': ('activate', self.on_rename_activate),
                'delete': ('activate', self.on_delete_activate),
                'statistics': ('activate', self.on_statistics_activate)}
        for signal in sigs:
            view.menu[signal].connect(sigs[signal][0], sigs[signal][1])

        col = gtk.TreeViewColumn('discs_column')

        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()

        # make cell text editabe
        cell.set_property('editable', True)
        cell.connect('edited', self.on_editing_done, self.discs_model)
        # TODO: find a way how to disable default return keypress on editable
        # fields

        col.pack_start(cellpb, False)
        col.pack_start(cell, True)

        col.set_attributes(cellpb, stock_id=2)
        col.set_attributes(cell, text=1)

        view['discs'].append_column(col)
        view['discs'].show()

    # treeview signals
    def on_discs_button_press_event(self, treeview, event):
        """
        Handle right click on discs treeview - show popup menu.
        """
        LOG.debug(self.on_discs_button_press_event.__doc__.strip())
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))

        if event.button == 3:
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

    def on_discs_cursor_changed(self, treeview):
        """
        Show files on right treeview, after clicking the left disc treeview.
        """
        LOG.debug(self.on_discs_cursor_changed.__doc__.strip())
        selection = treeview.get_selection()
        path = selection.get_selected_rows()[1][0]
        self.model.files.refresh(self.discs_model.get_value(\
                self.discs_model.get_iter(path), 0))

    def on_discs_key_release_event(self, treeview, event):
        """
        Watch for specific keys
        """
        LOG.debug(self.on_discs_key_release_event.__doc__.strip())
        if gtk.gdk.keyval_name(event.keyval) == 'Menu':
            LOG.debug('Menu key pressed')
            self._popup_menu(treeview.get_selection(), event, 0)
            return True
        return False

    def on_discs_row_activated(self, treeview, path, treecolumn):
        """
        If possible, expand or collapse branch of discs tree
        """
        LOG.debug(self.on_discs_row_activated.__doc__.strip())
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path, False)

    def on_editing_done(self, cell, path, new_text, model):
        """
        Store changed filename text
        """
        LOG.debug(self.on_editing_done.__doc__.strip())
        model[path][0].filename = new_text
        model[path][1] = new_text
        return

    # popup menu signals
    def on_expand_all_activate(self, menu_item):
        """
        Expand all
        """
        LOG.debug(self.on_expand_all_activate.__doc__.strip())
        self.view['discs'].expand_all()

    def on_collapse_all_activate(self, menu_item):
        """
        Collapse all
        """
        LOG.debug(self.on_collapse_all_activate.__doc__.strip())
        self.view['discs'].collapse_all()

    def on_update_activate(self, menu_item):
        """
        Trigger update specified tree entry
        """
        LOG.debug(self.on_update_activate.__doc__.strip())
        raise NotImplementedError

    def on_rename_activate(self, menu_item):
        """
        Rename disk or directory
        """
        LOG.debug(self.on_rename_activate.__doc__.strip())
        treeview = self.view['discs']
        selection = treeview.get_selection()
        path = selection.get_selected_rows()[1][0]
        treeview.set_cursor(path, treeview.get_column(0), start_editing=True)

    def on_delete_activate(self, menu_item):
        """
        Delete disk or directory from catalog
        """
        LOG.debug(self.on_delete_activate.__doc__.strip())
        raise NotImplementedError

    def on_statistics_activate(self, menu_item):
        """
        Show statistics for selected item
        """
        LOG.debug(self.on_statistics_activate.__doc__.strip())
        raise NotImplementedError

    # observable properties
    def property_currentdir_value_change(self, model, old, new):
        """
        Change of a current dir signalized by other controllers/models
        """
        LOG.debug(self.property_currentdir_value_change.__doc__.strip())
        self._set_cursor_to_obj_position(new)

    # private methods
    def _popup_menu(self, selection, event, button):
        """
        Popup menu for discs treeview. Gather information from discs model,
        and trigger menu popup.
        """
        LOG.debug(self._popup_menu.__doc__.strip())
        if selection is None:
            self.view.menu.set_menu_items_sensitivity(False)
        else:
            model, list_of_paths = selection.get_selected_rows()

            for path in list_of_paths:
                self.view.menu.set_menu_items_sensitivity(True)
                self.view.menu.set_update_sensitivity(model.get_value(\
                        model.get_iter(path), 0).parent_id == 1)

        self.view.menu['discs_popup'].popup(None, None, None,
                                            button, event.time)

    def _set_cursor_to_obj_position(self, obj):
        """
        Set cursor/focus to specified object postion in Discs treeview.
        """
        path = self.model.discs.find_path(obj)
        self.view['discs'].expand_to_path(path)
        self.view['discs'].set_cursor(path)
