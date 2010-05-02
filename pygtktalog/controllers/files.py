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

    def register_view(self, view):
        """Default view registration stuff"""
        self.view['files'].set_model(self.model.discs)

        col = gtk.TreeViewColumn('kolumna2')

        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()

        col.pack_start(cellpb, False)
        col.pack_start(cell, True)

        col.set_attributes(cellpb, stock_id=0)
        col.set_attributes(cell, text=1)
        self.view['files'].append_column(col)

