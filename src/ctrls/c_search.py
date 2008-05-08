# This Python file uses the following encoding: utf-8
#
#  Author: Roman 'gryf' Dobosz  gryf@elysium.pl
#
#  Copyright (C) 2007 by Roman 'gryf' Dobosz
#
#  This file is part of pyGTKtalog.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

#  -------------------------------------------------------------------------

from gtkmvc import Controller

import gtk

class SearchController(Controller):
    """Controller for main application window"""

    def __init__(self, model):
        """Initialize controller"""
        Controller.__init__(self, model)
        return

    def register_view(self, view):
        Controller.register_view(self, view)

        # Setup TreeView result widget, as columned list
        v = self.view['result']
        v.set_model(self.model.search_list)

        v.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        c = gtk.TreeViewColumn('Disc', gtk.CellRendererText(), text=1)
        c.set_sort_column_id(1)
        c.set_resizable(True)
        v.append_column(c)

        c = gtk.TreeViewColumn('Filename')
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        c.pack_start(cellpb, False)
        c.pack_start(cell, True)
        c.set_attributes(cellpb, stock_id=7)
        c.set_attributes(cell, text=2)
        c.set_sort_column_id(2)
        c.set_resizable(True)
        v.append_column(c)

        c = gtk.TreeViewColumn('Path', gtk.CellRendererText(), text=3)
        c.set_sort_column_id(3)
        c.set_resizable(True)
        v.append_column(c)

        c = gtk.TreeViewColumn('Size', gtk.CellRendererText(), text=4)
        c.set_sort_column_id(4)
        c.set_resizable(True)
        v.append_column(c)

        c = gtk.TreeViewColumn('Date', gtk.CellRendererText(), text=5)
        c.set_sort_column_id(5)
        c.set_resizable(True)
        v.append_column(c)
        v.set_search_column(2)

        # combobox
        self.view['comboboxentry'].set_model(self.model.search_history)
        self.view['comboboxentry'].set_text_column(0)
        # statusbar
        self.context_id = self.view['statusbar'].get_context_id('search')
        self.view['statusbar'].pop(self.context_id)
        self.view['search_window'].show()
        self.model.search_created = True;
        return

    #########################################################################
    # Connect signals from GUI, like menu objects, toolbar buttons and so on.
    def on_search_window_delete_event(self, window, event):
        """if window was closed, reset attributes"""
        self.model.point = None
        self.model.search_created = False;
        return False

    def on_close_clicked(self, button):
        """close search window"""
        self.model.point = None
        self.model.search_created = False;
        self.view['search_window'].destroy()

    def on_search_activate(self, entry):
        """find button or enter pressed on entry search. Do the search"""
        search_txt = self.view['search_entry'].get_text()
        found = self.model.search(search_txt)
        self.model.add_search_history(search_txt)

        if found == 0:
            msg = "No files found."
        elif found == 1:
            msg = "Found 1 file."
        else:
            msg = "Found %d files." % found

        self.view['statusbar'].push(self.context_id, "%s" % msg)

    def on_result_row_activated(self, treeview, path, treecolumn):
        """result treeview row activated, change models 'point' observable
        variable to id of elected item. rest is all in main controler hands."""
        model = treeview.get_model()
        s_iter = model.get_iter(path)
        self.model.point = model.get_value(s_iter, 0)

    def on_comboboxentry_changed(self, comboentry):
        """comboentry has changed, fill entry with selected item"""
        print "TODO: implement me!"

    #####################
    # observed properetis

    #########################
    # private class functions

    pass # end of class
