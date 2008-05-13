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

import gtk

from gtkmvc import Controller
import views.v_dialogs as Dialogs

class SearchController(Controller):
    """Controller for main application window"""

    def __init__(self, model):
        """Initialize controller"""
        Controller.__init__(self, model)
        self.search_string = ""
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
        self.search_string = search_txt
        found = self.model.search(search_txt)
        self.model.add_search_history(search_txt)
        self.__set_status_bar(found)

    def on_result_row_activated(self, treeview, path, treecolumn):
        """result treeview row activated, change models 'point' observable
        variable to id of elected item. rest is all in main controler hands."""
        model = treeview.get_model()
        s_iter = model.get_iter(path)
        self.model.point = model.get_value(s_iter, 0)

    def on_result_button_release_event(self, tree, event):
        if event.button == 3: # Right mouse button. Show context menu.
            try:
                selection = tree.get_selection()
                model, list_of_paths = selection.get_selected_rows()
            except TypeError:
                list_of_paths = []

            if len(list_of_paths) == 0:
                # try to select item under cursor
                try:
                    path, column, x, y = tree.get_path_at_pos(int(event.x),
                                                              int(event.y))
                except TypeError:
                    # failed, do not show any popup and return
                    tree.get_selection().unselect_all()
                    return False
                selection.select_path(path[0])

            if len(list_of_paths) > 1:
                self.view['add_image'].set_sensitive(False)
                self.view['rename'].set_sensitive(False)
                self.view['edit'].set_sensitive(False)
            else:
                self.view['add_image'].set_sensitive(True)
                self.view['rename'].set_sensitive(True)
                self.view['edit'].set_sensitive(True)
            self.view['files_popup'].popup(None, None, None, 0, 0)
            self.view['files_popup'].show_all()
            return True

    def on_add_tag_activate(self, menu_item):
        """Add tags to selected files"""
        tags = Dialogs.TagsDialog().run()
        if not tags:
            return
        ids = self.__get_tv_selection_ids(self.view['result'])
        for item_id in ids:
            self.model.add_tags(item_id, tags)
        
        self.model.unsaved_project = True
        return

    def on_delete_tag_activate(self, menu_item):
        ids = self.__get_tv_selection_ids(self.view['result'])
        if not ids:
            Dialogs.Inf("Remove tags", "No files selected",
                        "You have to select some files first.")
            return

        tags = self.model.get_tags_by_file_id(ids)
        if tags:
            d = Dialogs.TagsRemoveDialog(tags)
            retcode, retval = d.run()
            if retcode=="ok" and not retval:
                Dialogs.Inf("Remove tags", "No tags selected",
                            "You have to select any tag to remove from files.")
                return
            elif retcode == "ok" and retval:
                self.model.delete_tags(ids, retval)
                found = self.model.search(self.search_string)
                self.__set_status_bar(found)

    def on_add_thumb_activate(self, menu_item):
        image, only_thumbs = Dialogs.LoadImageFile().run()
        if not image:
            return
        ids = self.__get_tv_selection_ids(self.view['result'])
        for item_id in ids:
            self.model.add_thumbnail(image, item_id)
            
        self.model.unsaved_project = True
        return
        
    def on_remove_thumb_activate(self, menu_item):
        if self.model.config.confd['delwarn']:
            title = 'Delete thumbnails'
            question = 'Delete thumbnails?'
            description = "Thumbnails for selected items will be permanently"
            description += " removed from catalog."
            obj = Dialogs.Qst(title, question, description)
            if not obj.run():
                return
        try:
            ids = self.__get_tv_selection_ids(self.view['result'])
            for item_id in ids:
                self.model.del_thumbnail(item_id)
        except:
            if __debug__:
                print "c_search.py: on_remove_thumb_activate(): error on",
                print "getting selected items or removing thumbnails"
            return

        self.model.unsaved_project = True
        return

    def on_add_image_activate(self, menu_item):
        dialog = Dialogs.LoadImageFile(True)
        msg = "Don't copy images. Generate only thumbnails."
        toggle = gtk.CheckButton(msg)
        toggle.show()
        dialog.dialog.set_extra_widget(toggle)

        images, only_thumbs = dialog.run()
        if not images:
            return

        for image in images:
            try:
                selection = self.view['result'].get_selection()
                model, list_of_paths = selection.get_selected_rows()
                fid = model.get_value(model.get_iter(list_of_paths[0]), 0)
            except:
                try:
                    path, column = self.view['result'].get_cursor()
                    model = self.view['result'].get_model()
                    fiter = model.get_iter(path)
                    fid = model.get_value(fiter, 0)
                except:
                    return
            self.model.add_image(image, fid, only_thumbs)

            self.model.unsaved_project = True
        return

    def on_remove_image_activate(self, menu_item):
        if self.model.config.confd['delwarn']:
            title = 'Delete images'
            question = 'Delete all images?'
            description = 'All images for selected items will be permanently'
            description += ' removed from catalog.'
            obj = Dialogs.Qst(title, question, description)
            if not obj.run():
                return
        try:
            ids = self.__get_tv_selection_ids(self.view['result'])
            for item_id in ids:
                self.model.del_images(item_id)
        except:
            if __debug__:
                print "c_search.py: on_remove_thumb_activate(): error on",
                print "getting selected items or removing thumbnails"
            return

        self.model.unsaved_project = True
        return

    def on_edit_activate(self, menu_item):
        try:
            selection = self.view['result'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
            fid = model.get_value(model.get_iter(list_of_paths[0]), 0)
        except TypeError:
            if __debug__:
                print "c_main.py: on_edit2_activate(): 0",
                print "zaznaczonych wierszy"
            return

        val = self.model.get_file_info(fid)
        ret = Dialogs.EditDialog(val).run()
        if ret:
            self.model.rename(fid, ret['filename'])
            self.model.update_desc_and_note(fid,
                                            ret['description'], ret['note'])
            self.model.unsaved_project = True

    def on_delete_activate(self, menu_item):
        dmodel = self.model.discs_tree
        try:
            selection = self.view['result'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
        except TypeError:
            return

        if not list_of_paths:
            Dialogs.Inf("Delete files", "No files selected",
                        "You have to select at least one file to delete.")
            return

        if self.model.config.confd['delwarn']:
            description = "Selected files and directories will be "
            description += "permanently\n removed from catalog."
            obj = Dialogs.Qst("Delete files", "Delete files?", description)
            if not obj.run():
                return

        def foreach_searchtree(zmodel, zpath, ziter, d):
            if d[0] == zmodel.get_value(ziter, 0):
                d[1].append(zpath)
            return False

        for p in list_of_paths:
            val = model.get_value(model.get_iter(p), 0)
            if model.get_value(model.get_iter(p), 4) == self.model.DIR:
                # remove from disctree model aswell
                dpath = []
                dmodel.foreach(foreach_searchtree, (val, dpath))
                for dp in dpath:
                    dmodel.remove(dmodel.get_iter(dp))

            # delete from db
            self.model.delete(val)

        self.model.unsaved_project = True
        found = self.model.search(self.search_string)
        self.__set_status_bar(found)
        return

    def on_rename_activate(self, menu_item):
        try:
            selection = self.view['result'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
            fid = model.get_value(model.get_iter(list_of_paths[0]), 0)
        except TypeError:
            if __debug__:
                print "c_main.py: on_edit2_activate(): 0",
                print "zaznaczonych wierszy"
            return

        fid = model.get_value(model.get_iter(list_of_paths[0]), 0)
        name = model.get_value(model.get_iter(list_of_paths[0]),2)
        new_name = Dialogs.InputNewName(name).run()

        if __debug__:
            print "c_search.py: on_rename_activate(): label:", new_name

        if new_name and new_name != name:
            self.model.rename(fid, new_name)
            self.model.unsaved_project = True
        return

    #####################
    # observed properetis

    #########################
    # private class functions
    def __set_status_bar(self, found):
        """sets number of founded items in statusbar"""
        if found == 0:
            msg = "No files found."
        elif found == 1:
            msg = "Found 1 file."
        else:
            msg = "Found %d files." % found
        self.view['statusbar'].push(self.context_id, "%s" % msg)
        
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
                print "c_search.py: __get_tv_selection_ids(): error on",
                print "getting selected items"
            return
        return None

    pass # end of class
