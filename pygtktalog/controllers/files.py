"""
    Project: pyGTKtalog
    Description: Controller for Files TreeView
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-30
"""
import gtk

from gtkmvc import Controller


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
        view['files'].drag_source_set(gtk.gdk.BUTTON1_MASK,
                                      self.DND_TARGETS,
                                      gtk.gdk.ACTION_COPY)

