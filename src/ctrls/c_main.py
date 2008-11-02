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

__version__ = "1.0 RC2"
LICENCE = open('LICENCE').read()

import os.path
from os import popen
from utils import deviceHelper
from gtkmvc import Controller

from c_config import ConfigController
from views.v_config import ConfigView

from c_search import SearchController
from views.v_search import SearchView

import views.v_dialogs as Dialogs

from views.v_image import ImageView

import gtk
import pango

class MainController(Controller):
    """Controller for main application window"""
    scan_cd = False
    widgets_all = ('tag_path_box', 'hpaned1',
                       'file1', 'edit1', 'view1', 'help1',
                           'add_cd', 'add_directory1', 'del_all_images',
                           'del_all_thumb', 'stat1',
                       'tb_new','tb_open', 'tb_save', 'tb_addcd', 'tb_adddir',
                       'tb_find', 'tb_quit')
    widgets_cancel = ('cancel','cancel1')

    def __init__(self, model):
        """Initialize controller"""
        self.DND_TARGETS = [('files_tags', 0, 69)]
        Controller.__init__(self, model)
        self.hovering = False
        self.first = True
        return

    def register_view(self, view):
        Controller.register_view(self, view)

        # Make not active "Cancel" button and menu_item
        for widget in self.widgets_cancel:
            self.view[widget].set_sensitive(False)

        # hide "debug" button, if production
        # (i.e. python OT running with -OO option)
        if __debug__:
            self.view['debugbtn'].show()
        else:
            self.view['debugbtn'].hide()

        # load configuration/defaults and set it to properties
        bo = self.model.config.confd['showtoolbar']
        self.view['toolbar1'].set_active(bo)
        if bo:
            self.view['maintoolbar'].show()
        else:
            self.view['maintoolbar'].hide()
        statusbar_state = self.model.config.confd['showstatusbar']
        self.view['status_bar1'].set_active(statusbar_state)
        if self.model.config.confd['showstatusbar']:
            self.view['statusprogress'].show()
        else:
            self.view['statusprogress'].hide()
        self.view['hpaned1'].set_position(self.model.config.confd['h'])
        self.view['vpaned1'].set_position(self.model.config.confd['v'])
        self.view['main'].resize(self.model.config.confd['wx'],
                                 self.model.config.confd['wy'])

        # initialize statusbar
        context = self.view['mainStatus'].get_context_id('detailed res')
        self.context_id = context
        self.statusbar_id = self.view['mainStatus'].push(self.context_id,
                                                         "Idle")

        # make tag_cloud_textview recive dnd signals
        self.view['tag_cloud_textview'].drag_dest_set(gtk.DEST_DEFAULT_ALL,
                          self.DND_TARGETS,
                          gtk.gdk.ACTION_COPY)

        # initialize treeviews
        self.__setup_disc_treeview()
        self.__setup_files_treeview()
        self.__setup_exif_treeview()

        # in case passing catalog filename in command line, unlock gui
        if self.model.filename:
            self.__activate_ui(self.model.filename)

        # generate recent menu
        self.__generate_recent_menu()

        self.view['tag_cloud_textview'].connect("populate-popup",
                                           self.on_tag_cloud_textview_popup)
        # in case model has opened file, register tags
        if self.model.db_tmp_path:
            self.__tag_cloud()
        else:
            self.model.new()
            #self.__activate_ui()

        # Show main window
        self.view['main'].show();
        self.view['main'].drag_dest_set(0, [], 0)
        return

    #########################################################################
    # Connect signals from GUI, like menu objects, toolbar buttons and so on.
    def on_tag_cloud_textview_drag_drop(self, wid, context, x, y, time):
        context.finish(True, False, time)
        return True

    def on_tag_cloud_textview_drag_motion(self, filestv, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_COPY, time)
        iter = filestv.get_iter_at_location(x, y)
        buff = filestv.get_buffer()
        tag_table = buff.get_tag_table()

        # clear weight of tags
        def foreach_tag(texttag, user_data):
            """set every text tag's weight to normal"""
            texttag.set_property("underline", pango.UNDERLINE_NONE)
        tag_table.foreach(foreach_tag, None)

        try:
            tag = iter.get_tags()[0]
            tag.set_property("underline", pango.UNDERLINE_LOW)
        except:
            pass
        return True

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
                id = model.get_value(model.get_iter(path), 0)
                ids.append(id)
            string = str(tuple(ids)).replace(",)", ")")
            selection.set(selection.target, 8, string)

    def on_tag_cloud_textview_popup(self, textview, menu):
        menu = None
        return True

    def on_tag_cloud_textview_event_after(self, textview, event):
        """check, if and what tag user clicked. generate apropriate output
        in files treview"""
        if event.type != gtk.gdk.BUTTON_RELEASE:
            return False
        if event.button != 1:
            return False

        buff = textview.get_buffer()
        try:
            (start, end) = buff.get_selection_bounds()
        except ValueError:
            pass
        else:
            if start.get_offset() != end.get_offset():
                return False

        # get the iter at the mouse position
        (x, y) = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
                                              int(event.x), int(event.y))
        iterator = textview.get_iter_at_location(x, y)

        tags = iterator.get_tags()

        if len(tags) == 1:
            tag = tags[0]
            self.model.add_tag_to_path(tag.get_property('name'))
            self.view['tag_path_box'].show()

            # fill the path of tag
            self.view['tag_path'].set_text('')
            temp = self.model.selected_tags.values()
            self.model.refresh_discs_tree()
            #self.on_discs_cursor_changed(textview)

            temp.sort()
            for tag1 in temp:
                txt = self.view['tag_path'].get_text()
                if txt == '':
                    self.view['tag_path'].set_text(tag1)
                else:
                    self.view['tag_path'].set_text(txt + ", " +tag1)
            self.__tag_cloud()
        self.model.get_root_entries()
        self.__set_files_hiden_columns_visible(True)
        self.view['files'].set_model(self.model.files_list)
        self.__hide_details()

    def on_tag_cloud_textview_drag_data_received(self, widget, context, x, y,
                                                 selection, targetType, time):
        """recive data from source TreeView"""
        if targetType == self.DND_TARGETS[0][2]:
            iter = widget.get_iter_at_location(x, y)
            ids = selection.data.rstrip(")").lstrip("(").split(",")
            try:
                tag = iter.get_tags()[0]
                for id in ids:
                    it = int(tag.get_property('name'))
                    tn = self.model.get_tag_by_id(it)
                    self.model.add_tags(int(id.strip()), tn)
            except:
                if selection.data:
                    tags = Dialogs.TagsDialog().run()
                    if not tags:
                        return
                    for id in ids:
                        self.model.add_tags(int(id.strip()), tags)

        self.__tag_cloud()

    def on_edit2_activate(self, menu_item):
        try:
            selection = self.view['files'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
            id = model.get_value(model.get_iter(list_of_paths[0]), 0)
        except TypeError:
            if __debug__:
                print "c_main.py: on_edit2_activate(): 0",
                print "zaznaczonych wierszy"
            return

        val = self.model.get_file_info(id)
        ret = Dialogs.EditDialog(val).run()
        if ret:
            self.model.rename(id, ret['filename'])
            self.model.update_desc_and_note(id,
                                            ret['description'], ret['note'])
            self.__get_item_info(id)
            self.model.unsaved_project = True
            self.__set_title(filepath=self.model.filename, modified=True)

    def on_add_thumb1_activate(self, menu_item):
        image, only_thumbs = Dialogs.LoadImageFile().run()
        if not image:
            return
        selection = self.view['files'].get_selection()
        model, list_of_paths = selection.get_selected_rows()
        for path in list_of_paths:
            id = model.get_value(model.get_iter(path), 0)
            self.model.add_thumbnail(image, id)
        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        self.__get_item_info(id)
        return

    def on_remove_thumb1_activate(self, menu_item):
        if self.model.config.confd['delwarn']:
            title = 'Delete thumbnails'
            question = 'Delete thumbnails?'
            description = "Thumbnails for selected items will be permanently"
            description += " removed from catalog."
            obj = Dialogs.Qst(title, question, description)
            if not obj.run():
                return
        try:
            selection = self.view['files'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
            for path in list_of_paths:
                id = model.get_value(model.get_iter(path), 0)
                self.model.del_thumbnail(id)
        except:
            if __debug__:
                print "c_main.py: on_remove_thumb1_activate(): error on",
                print "getting selected items or removing thumbnails"
            return

        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        self.__get_item_info(id)
        return

    def on_remove_image1_activate(self, menu_item):
        if self.model.config.confd['delwarn']:
            title = 'Delete images'
            question = 'Delete all images?'
            description = 'All images for selected items will be permanently'
            description += ' removed from catalog.'
            obj = Dialogs.Qst(title, question, description)
            if not obj.run():
                return
        try:
            selection = self.view['files'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
            for path in list_of_paths:
                id = model.get_value(model.get_iter(path), 0)
                self.model.del_images(id)
        except:
            if __debug__:
                print "c_main.py: on_remove_thumb1_activate(): error on",
                print "getting selected items or removing thumbnails"
            return

        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        self.__get_item_info(id)
        return

    def on_images_item_activated(self, iconview, path):
        model = iconview.get_model()
        iter = model.get_iter(path)
        id = model.get_value(iter, 0)
        img = self.model.get_image_path(id)
        if img:
            if self.model.config.confd['imgview'] and \
            len(self.model.config.confd['imgprog'])>0:
                popen("%s %s" % (self.model.config.confd['imgprog'], img))
            else:
                ImageView(img)
        else:
            Dialogs.Inf("Image view", "No Image",
                        "Image file does not exist.")

    def on_rename1_activate(self, widget):
        model, iter = self.view['discs'].get_selection().get_selected()
        name = model.get_value(iter, 1)
        id = model.get_value(iter, 0)
        new_name = Dialogs.InputNewName(name).run()

        if __debug__:
            print "c_main.py: on_rename1_activate(): label:", new_name

        if new_name and new_name != name:
            self.model.rename(id, new_name)
            self.model.unsaved_project = True
            self.__set_title(filepath=self.model.filename, modified=True)
        return True

    def on_rename2_activate(self, widget):
        try:
            selection = self.view['files'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
        except TypeError:
            return

        if len(list_of_paths) != 1:
            return

        fid = model.get_value(model.get_iter(list_of_paths[0]), 0)
        name = model.get_value(model.get_iter(list_of_paths[0]),1)

        new_name = Dialogs.InputNewName(name).run()
        if __debug__:
            print "c_main.py: on_rename1_activate(): label:", new_name

        if new_name and new_name != name:
            self.model.rename(fid, new_name)
            self.__get_item_info(fid)
            self.__set_title(filepath=self.model.filename, modified=True)

        #try:
        #    path, column = self.view['discs'].get_cursor()
        #    iter = model.get_iter(path)
        #    self.model.get_root_entries(model.get_value(iter, 0))
        #except TypeError:
        #    self.model.get_root_entries(1)
        #    return

        return

    def on_tag_cloud_textview_motion_notify_event(self, widget):
        if __debug__:
            print "c_main.py: on_tag_cloud_textview_motion_notify_event():"
        w = self.view['tag_cloud_textview'].get_window(gtk.TEXT_WINDOW_TEXT)
        if w:
            w.set_cursor(None)

    def on_clear_clicked(self, w):
        self.view['tag_path_box'].hide()
        self.model.selected_tags = []
        self.model.refresh_discs_tree()
        self.__set_files_hiden_columns_visible(False)

        # cleanup files and detiles
        try:
            self.model.files_list.clear()
        except:
            pass
        self.__hide_details()
        self.on_discs_cursor_changed(w)
        self.__tag_cloud()

    def on_tag_cloud_textview_drag_leave(self, textview, dragcontext, time):
        """clean up tags properties"""
        buff = textview.get_buffer()
        tag_table = buff.get_tag_table()

        # clear weight of tags
        def foreach_tag(texttag, user_data):
            """set every text tag's weight to normal"""
            texttag.set_property("underline", pango.UNDERLINE_NONE)
        tag_table.foreach(foreach_tag, None)

    # NOTE: text view "links" functions
    def on_tag_cloud_textview_visibility_notify_event(self, textview, event):
        (wx, wy, mod) = textview.window.get_pointer()
        (bx, by) = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
                                                     wx, wy)
        self.check_hovering(bx, by)
        return False

    def check_hovering(self, x, y):
        """Check if the mouse is above a tagged link and if yes show
           a hand cursor"""
        _hovering = False
        textview = self.view['tag_cloud_textview']
        # get the iter at the mouse position
        iter = textview.get_iter_at_location(x, y)

        # set _hovering if the iter has the tag "url"
        tags = iter.get_tags()
        for tag in tags:
            _hovering = True
            break

        # change the global hovering state
        if _hovering != self.hovering or self.first == True:
            self.first = False
            self.hovering = _hovering
            # Set the appropriate cursur icon
            if self.hovering:
                textview.get_window(gtk.TEXT_WINDOW_TEXT).\
                        set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
            else:
                textview.get_window(gtk.TEXT_WINDOW_TEXT).\
                        set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))

    def on_tag_cloud_click(self, tag, textview, event, b_iter, data):
        """react on click on connected tag items"""
        tag_cloud = self.view['tag_cloud_textview']
        if event.type == gtk.gdk.BUTTON_RELEASE:
            self.model.add_tag_to_path(tag.get_property('name'))
            self.view['tag_path_box'].show()

            # fill the path of tag
            self.view['tag_path'].set_text('')
            temp = self.model.selected_tags.values()
            self.model.refresh_discs_tree()
            #self.on_discs_cursor_changed(textview)

            temp.sort()
            for tag1 in temp:
                txt = self.view['tag_path'].get_text()
                if txt == '':
                    self.view['tag_path'].set_text(tag1)
                else:
                    self.view['tag_path'].set_text(txt + ", " +tag1)
            self.__tag_cloud()

    def on_main_destroy_event(self, window, event):
        """NOTE: quit / close window signal"""
        self.on_quit_activate(window)
        return True

    def on_quit_activate(self, widget):
        """Quit and save window parameters to config file"""
        # check if any unsaved project is on go.
        if self.model.unsaved_project and \
        self.model.config.confd['confirmquit']:
            title = 'Quit application - pyGTKtalog'
            question = 'Do you really want to quit?'
            description = "Current database is not saved, any changes will "
            description += "be lost."
            if not Dialogs.Qst(title, question, description).run():
                return
        self.__store_settings()
        self.model.cleanup()
        gtk.main_quit()
        return False

    def on_new_activate(self, widget):
        """Create new database file"""
        if self.model.unsaved_project:
            title = 'Unsaved data - pyGTKtalog'
            question = "Do you want to abandon changes?"
            desc = "Current database is not saved, any changes will be lost."
            if not Dialogs.Qst(title, question, desc).run():
                return
        self.model.new()

        # cleanup files and details
        try:
            self.model.files_list.clear()
        except:
            pass
        self.__hide_details()
        self.view['tag_path_box'].hide()
        self.__activate_ui()
        self.__tag_cloud()

    def on_add_cd_activate(self, widget, label=None, current_id=None):
        """Add directory structure from cd/dvd disc"""
        mount = deviceHelper.volmount(self.model.config.confd['cd'])
        if mount == 'ok':
            guessed_label = deviceHelper.volname(self.model.config.confd['cd'])
            if not label:
                label = Dialogs.InputDiskLabel(guessed_label).run()
            if label:
                self.scan_cd = True
                for widget in self.widgets_all:
                    self.view[widget].set_sensitive(False)
                self.model.source = self.model.CD
                self.model.scan(self.model.config.confd['cd'], label,
                                current_id)
                self.model.unsaved_project = True
                self.__set_title(filepath=self.model.filename, modified=True)
            else:
                deviceHelper.volumount(self.model.config.confd['cd'])
            return True
        else:
            Dialogs.Wrn("Error mounting device - pyGTKtalog",
                        "Cannot mount device pointed to %s" %
                        self.model.config.confd['cd'],
                        "Last mount message:\n%s" % mount)
            return False

    def on_add_directory_activate(self, widget, path=None, label=None,
                                   current_id=None):
        """Show dialog for choose drectory to add from filesystem."""
        if not label or not path:
            res = Dialogs.PointDirectoryToAdd().run()
            if res != (None, None):
                path = res[1]
                label = res[0]
            else:
                return False

        self.scan_cd = False
        self.model.source = self.model.DR
        self.model.scan(path, label, current_id)
        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        return

    # NOTE: about
    def on_about1_activate(self, widget):
        """Show about dialog"""
        Dialogs.Abt("pyGTKtalog", __version__, "About",
                    ["Roman 'gryf' Dobosz"], LICENCE)
        return

    def on_preferences_activate(self, widget):
        c = ConfigController(self.model.config)
        v = ConfigView(c)
        return

    def on_status_bar1_activate(self, widget):
        """Toggle visibility of statusbat and progress bar."""
        activity = self.view['status_bar1'].get_active()
        self.model.config.confd['showstatusbar'] = activity
        if self.view['status_bar1'].get_active():
            self.view['statusprogress'].show()
        else:
            self.view['statusprogress'].hide()

    def on_toolbar1_activate(self, widget):
        """Toggle visibility of toolbar bar."""
        activity = self.view['toolbar1'].get_active()
        self.model.config.confd['showtoolbar'] = activity
        if self.view['toolbar1'].get_active():
            self.view['maintoolbar'].show()
        else:
            self.view['maintoolbar'].hide()

    def on_save_activate(self, widget):
        """Save catalog to file"""
        if self.model.filename:
            self.model.save()
            self.__set_title(filepath=self.model.filename)
        else:
            self.on_save_as_activate(widget)

    def on_save_as_activate(self, widget):
        """Save database to file under different filename."""
        initial_path = None
        if self.model.config.recent[0]:
            initial_path = os.path.dirname(self.model.config.recent[0])

        path = Dialogs.ChooseDBFilename(initial_path).run()
        if path:
            ret, err = self.model.save(path)
            if ret:
                self.model.config.add_recent(path)
                self.__set_title(filepath=path)
            else:
                Dialogs.Err("Error writing file - pyGTKtalog",
                            "Cannot write file %s." % path, "%s" % err)

    def on_stat1_activate(self, menu_item, selected_id=None):
        data = self.model.get_stats(selected_id)
        label = Dialogs.StatsDialog(data).run()

    def on_statistics1_activate(self, menu_item):
        model = self.view['discs'].get_model()
        try:
            path, column = self.view['discs'].get_cursor()
            selected_iter = self.model.discs_tree.get_iter(path)
        except:
            return

        selected_id = self.model.discs_tree.get_value(selected_iter, 0)
        self.on_stat1_activate(menu_item, selected_id)

    def on_open_activate(self, widget, path=None):
        """Open catalog file"""
        confirm = self.model.config.confd['confirmabandon']
        if self.model.unsaved_project and confirm:
            obj = Dialogs.Qst('Unsaved data - pyGTKtalog',
                              'There is not saved database',
                              'Pressing "Ok" will abandon catalog.')
            if not obj.run():
                return

        initial_path = None
        if self.model.config.recent and self.model.config.recent[0]:
            initial_path = os.path.dirname(self.model.config.recent[0])

        if not path:
            path = Dialogs.LoadDBFile(initial_path).run()

        # cleanup files and details
        try:
            self.model.files_list.clear()
        except:
            pass
        self.__hide_details()
        self.view['tag_path_box'].hide()
        buf = self.view['tag_cloud_textview'].get_buffer()
        buf.set_text('')
        self.view['tag_cloud_textview'].set_buffer(buf)

        if path:
            if not self.model.open(path):
                Dialogs.Err("Error opening file - pyGTKtalog",
                            "Cannot open file %s." % path)
            else:
                self.__generate_recent_menu()
                self.__activate_ui(path)
                self.__tag_cloud()
        return

    def on_discs_cursor_changed(self, widget):
        """Show files on right treeview, after clicking the left disc
        treeview."""
        model = self.view['discs'].get_model()
        path, column = self.view['discs'].get_cursor()
        if path:
            iter = self.model.discs_tree.get_iter(path)
            id = self.model.discs_tree.get_value(iter, 0)
            self.__set_files_hiden_columns_visible(False)
            self.model.get_root_entries(id)
            self.__get_item_info(id)

        return

    def on_discs_row_activated(self, treeview, path, treecolumn):
        """If possible, expand or collapse branch of discs tree"""
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path, False)
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

    def on_images_key_release_event(self, iconview, event):
        if gtk.gdk.keyval_name(event.keyval) == 'Menu':
            self.__popup_menu(event, 'img_popup')
            return True
        return False

    def on_images_button_press_event(self, iconview, event):
        #try:
        #    path_and_cell = iconview.get_item_at_pos(int(event.x),
        #                                             int(event.y))
        #except TypeError:
        #    return False

        if event.button == 3: # Right mouse button. Show context menu.
            #try:
            #    iconview.select_path(path_and_cell[0])
            #except TypeError:
            #    return False

            self.__popup_menu(event, 'img_popup')
            return True
        return False

    def on_img_delete_activate(self, menu_item):
        """delete selected images (with thumbnails)"""
        list_of_paths = self.view['images'].get_selected_items()
        if not list_of_paths:
            Dialogs.Inf("Delete images", "No images selected",
                        "You have to select at least one image to delete.")
            return

        if self.model.config.confd['delwarn']:
            obj = Dialogs.Qst('Delete images', 'Delete selected images?',
                  'Selected images will be permanently removed from catalog.')
            if not obj.run():
                return

        model = self.view['images'].get_model()
        ids = []
        for path in list_of_paths:
            iterator = model.get_iter(path)
            ids.append(model.get_value(iterator, 0))

        for fid in ids:
            self.model.delete_image(fid)

        # refresh files tree
        try:
            path, column = self.view['files'].get_cursor()
            model = self.view['files'].get_model()
            iterator = model.get_iter(path)
            fid = model.get_value(iterator, 0)
            self.__get_item_info(fid)
        except:
            pass

        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        return

    def on_img_save_activate(self, menu_item):
        """export images (not thumbnails) into desired direcotry"""
        dialog = Dialogs.SelectDirectory("Choose directory to save images")
        filepath = dialog.run()

        if not filepath:
            return

        list_of_paths = self.view['images'].get_selected_items()
        model = self.view['images'].get_model()

        count = 0

        if len(list_of_paths) == 0:
            # no picture was selected. default to save all of them
            for image in model:
                if self.model.save_image(image[0], filepath):
                    count += 1
        else:
            # some pictures was selected, save them
            for path in list_of_paths:
                icon_iter = model.get_iter(path)
                img_id = model.get_value(icon_iter, 0)
                if self.model.save_image(img_id, filepath):
                    count += 1

        if count > 0:
            Dialogs.Inf("Save images",
                        "%d images was succsefully saved." % count,
                        "Images are placed in directory:\n%s." % filepath)
        else:
            description = "Images probably don't have real images - only"
            description += " thumbnails."
            Dialogs.Inf("Save images",
                        "No images was saved.",
                        description)
        return

    def on_img_thumbset_activate(self, menu_item):
        """set selected image as thumbnail"""
        list_of_paths = self.view['images'].get_selected_items()

        if not list_of_paths:
            Dialogs.Inf("Set thumbnail", "No image selected",
                        "You have to select one image to set as thumbnail.")
            return
        if len(list_of_paths) >1:
            Dialogs.Inf("Set thumbnail", "To many images selected",
                        "You have to select one image to set as thumbnail.")
            return

        model = self.view['images'].get_model()
        iter = model.get_iter(list_of_paths[0])
        id = model.get_value(iter, 0)
        self.model.set_image_as_thumbnail(id)

        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        return

    def on_img_add_activate(self, menu_item):
        self.on_add_image1_activate(menu_item)

    def on_thumb_box_button_press_event(self, widget, event):
        if event.button == 3:
            self.__popup_menu(event, 'th_popup')

    def on_discs_button_press_event(self, treeview, event):
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
            menu_items = ['update1','rename1','delete2', 'statistics1']
            for menu_item in menu_items:
                self.view[menu_item].set_sensitive(not not ids)

            # checkout, if we dealing with disc or directory
            # if ancestor is 'root', then activate "update" menu item
            treeiter = self.model.discs_tree.get_iter(path)
            ancestor = self.model.discs_tree.get_value(treeiter, 3) == 1
            self.view['update1'].set_sensitive(ancestor)

            self.__popup_menu(event)

    def on_expand_all1_activate(self, menu_item):
        self.view['discs'].expand_all()
        return

    def on_collapse_all1_activate(self, menu_item):
        self.view['discs'].collapse_all()
        return

    def on_files_button_press_event(self, tree, event):
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
                self.view['add_image1'].set_sensitive(False)
                self.view['rename2'].set_sensitive(False)
                self.view['edit2'].set_sensitive(False)
            else:
                self.view['add_image1'].set_sensitive(True)
                self.view['rename2'].set_sensitive(True)
                self.view['edit2'].set_sensitive(True)
            self.__popup_menu(event, 'files_popup')
            return True

    def on_files_cursor_changed(self, treeview):
        """Show details of selected file/directory"""
        file_id = self.__get_tv_id_under_cursor(treeview)
        self.__get_item_info(file_id)
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
            self.__popup_menu(event, 'files_popup')

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

        ids = self.__get_tv_selection_ids(self.view['files'])

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

    def on_cancel_clicked(self, widget):
        """When scanning thread is runing and user push the cancel button,
        models abort attribute trigger cancelation for scan operation"""
        self.model.abort = True
        return

    def on_find_activate(self, widget):
        """search button/menu activated. Show search window"""
        if not self.model.search_created:
            c = SearchController(self.model)
            v = SearchView(c)
        return

    # NOTE: recent signal
    def recent_item_response(self, path):
        self.on_open_activate(self, path)
        return

    # NOTE: add tags / images
    def on_delete_tag2_activate(self, menu_item):
        pass

    def on_delete_tag_activate(self, menu_item):
        ids = self.__get_tv_selection_ids(self.view['files'])
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
                self.model.get_root_entries()
                self.view['files'].set_model(self.model.files_list)
                self.__tag_cloud()
        return

    def on_add_tag1_activate(self, menu_item):
        tags = Dialogs.TagsDialog().run()
        if not tags:
            return
        ids = self.__get_tv_selection_ids(self.view['files'])
        for id in ids:
            self.model.add_tags(id, tags)

        self.__tag_cloud()
        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        self.__get_item_info(id)
        return

    def on_add_image1_activate(self, menu_item):
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
                selection = self.view['files'].get_selection()
                model, list_of_paths = selection.get_selected_rows()
                id = model.get_value(model.get_iter(list_of_paths[0]), 0)
            except:
                try:
                    path, column = self.view['files'].get_cursor()
                    model = self.view['files'].get_model()
                    iter = model.get_iter(path)
                    id = model.get_value(iter, 0)
                except:
                    return
            self.model.add_image(image, id, only_thumbs)

            self.model.unsaved_project = True
            self.__set_title(filepath=self.model.filename, modified=True)

        self.__get_item_info(id)
        return

    def on_update1_activate(self, menu_item):
        """Update disc under cursor position"""
        path, column = self.view['discs'].get_cursor()
        model = self.view['discs'].get_model()

        # determine origin label and filepath
        filepath, label = self.model.get_label_and_filepath(path)

        fid = model.get_value(model.get_iter(path), 0)

        if self.model.get_source(path) == self.model.CD:
            self.on_add_cd_activate(menu_item, label, fid)
        elif self.model.get_source(path) == self.model.DR:
            self.on_add_directory_activate(menu_item, filepath, label, fid)

        return

    def on_delete1_activate(self, menu_item):
        """Main menu delete dispatcher"""
        if self.view['files'].is_focus():
            self.on_delete3_activate(menu_item)
        if self.view['discs'].is_focus():
            self.on_delete2_activate(menu_item)
        if self.view['images'].is_focus():
            self.on_img_delete_activate(menu_item)

    def on_delete2_activate(self, menu_item):
        try:
            selection = self.view['discs'].get_selection()
            model, selected_iter = selection.get_selected()
        except:
            return

        if not selected_iter:
            Dialogs.Inf("Delete disc", "No disc selected",
                        "You have to select disc first before you " +\
                        "can delete it")
            return

        if self.model.config.confd['delwarn']:
            name = model.get_value(selected_iter, 1)
            obj = Dialogs.Qst('Delete %s' % name, 'Delete %s?' % name,
                              'Object will be permanently removed.')
            if not obj.run():
                return

        # remove from model
        path = model.get_path(selected_iter)
        fid = self.model.discs_tree.get_value(selected_iter, 0)
        model.remove(selected_iter)
        selection.select_path(path)

        if not selection.path_is_selected(path):
            row = path[0]-1
            if row >= 0:
                selection.select_path((row,))
                path = (row, )

        # delete from db
        self.model.delete(fid)

        # refresh files treeview
        try:
            id = model.get_value(model.get_iter(path), 0)
        except:
            id = model.get_value(model.get_iter_first(), 0)
        self.model.get_root_entries(id)

        # refresh file info view
        self.__get_item_info(id)

        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        return

    def on_delete3_activate(self, menu_item):
        """delete files selected on files treeview"""
        dmodel = self.model.discs_tree
        try:
            selection = self.view['files'].get_selection()
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

        def foreach_disctree(zmodel, zpath, ziter, d):
            if d[0] == zmodel.get_value(ziter, 0):
                d[1].append(zpath)
            return False

        ids = []
        for p in list_of_paths:
            val = model.get_value(model.get_iter(p), 0)
            ids.append(val)

        for fid in ids:
            # delete from db
            self.model.delete(fid)

        try:
            # try to select something
            selection = self.view['discs'].get_selection()
            model, list_of_paths = selection.get_selected_rows()
            if not list_of_paths:
                list_of_paths = [1]
            fiter = model.get_iter(list_of_paths[0])
            self.model.get_root_entries(model.get_value(fiter, 0))
        except TypeError:
            return

        buf = gtk.TextBuffer()
        self.view['description'].set_buffer(buf)
        self.view['thumb_box'].hide()
        self.view['exifinfo'].hide()
        self.view['img_container'].hide()

        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)
        return

    def on_th_delete_activate(self, menu_item):
        if self.model.config.confd['delwarn']:
            title = 'Delete thumbnail'
            question = 'Delete thumbnail?'
            dsc = "Current thumbnail will be permanently removed from catalog."
            obj = Dialogs.Qst(title, question, dsc)
            if not obj.run():
                return
        path, column = self.view['files'].get_cursor()
        model = self.view['files'].get_model()
        iter = model.get_iter(path)
        id = model.get_value(iter, 0)
        if id:
            self.model.del_thumbnail(id)
            self.__get_item_info(id)
            self.model.unsaved_project = True
            self.__set_title(filepath=self.model.filename, modified=True)
        return

    def on_del_all_images_activate(self, menu_item):
        if self.model.config.confd['delwarn']:
            title = 'Delete images'
            question = 'Delete all images?'
            dsc = "All images and it's thumbnails will be permanently removed"
            dsc += " from catalog."
            obj = Dialogs.Qst(title, question, dsc)
            if not obj.run():
                return

        self.model.delete_all_images()
        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)

        try:
            path, column = self.view['files'].get_cursor()
            model = self.view['files'].get_model()
            fiter = model.get_iter(path)
            fid = model.get_value(fiter, 0)
            if fid:
                self.__get_item_info(fid)
        except:
            pass
        return

    def on_del_all_thumb_activate(self, menu_item):
        if self.model.config.confd['delwarn']:
            title = 'Delete images'
            question = 'Delete all images?'
            dsc = "All images without thumbnails will be permanently removed"
            dsc += " from catalog."
            obj = Dialogs.Qst(title, question, dsc)
            if not obj.run():
                return

        self.model.del_all_thumbnail()
        self.model.unsaved_project = True
        self.__set_title(filepath=self.model.filename, modified=True)

        try:
            path, column = self.view['files'].get_cursor()
            model = self.view['files'].get_model()
            fiter = model.get_iter(path)
            fid = model.get_value(fiter, 0)
            if fid:
                self.__get_item_info(fid)
        except:
            pass
        return

    def on_edit1_activate(self, menu_item):
        """Make sufficient menu items sensitive in right cases"""
        # TODO: consolidate popup-menus with edit menu
        if  self.view['tag_cloud_textview'].is_focus():
            self.view['delete1'].set_sensitive(False)
        else:
            self.view['delete1'].set_sensitive(True)

    def on_debugbtn_clicked(self, widget):
        """Debug. To remove in stable version, including button in GUI"""
        if __debug__:
            print "\nc_main.py: on_debugbtn_clicked()"
            print "------"
            print "unsaved_project = %s" % self.model.unsaved_project
            print "filename = %s" % self.model.filename
            print "internal_filename = %s" % self.model.internal_dirname
            print "db_connection = %s" % self.model.db_connection
            print "abort = %s" % self.model.abort
            print "self.model.config.recent = %s" % self.model.config.recent
            print "source: %s" % self.model.source
            print "files have focus", self.view['files'].is_focus()
            print "discs have focus", self.view['discs'].is_focus()
            print "images have focus", self.view['images'].is_focus()
            c = self.view['files'].get_column(0)
            c.set_visible(not c.get_visible())
            c = self.view['files'].get_column(2)
            c.set_visible(not c.get_visible())

    #####################
    # observed properetis
    def property_point_value_change(self, model, old, new):
        """File was activated in search window through the observable
        property - select it on the discs and files treeview, and get
        file description"""

        if new:
            discs_tree = self.view['discs']
            discs_model = discs_tree.get_model()
            parent_id = self.model.get_parent_id(new)

            def foreach_disctree(model, path, iterator, data):
                """find path in model to desired value"""
                if model.get_value(iterator, 0) == data:
                    discs_tree.expand_to_path(path)
                    discs_tree.set_cursor(path)
                return False

            discs_model.foreach(foreach_disctree, parent_id)

            files_list = self.view['files']
            files_model = files_list.get_model()

            def foreach_fileslist(model, path, iterator, data):
                """find path in model to desired value"""
                if model.get_value(iterator, 0) == data:
                    files_list.set_cursor(path)
                    self.__get_item_info(data)
                return False

            files_model.foreach(foreach_fileslist, new)
        return

    def property_statusmsg_value_change(self, model, old, new):
        if self.statusbar_id:
            self.view['mainStatus'].remove(self.context_id, self.statusbar_id)
        self.statusbar_id = self.view['mainStatus'].push(self.context_id,
                                                         "%s" % new)
        return

    def property_busy_value_change(self, model, old, new):
        if new != old:
            for w in self.widgets_all:
                self.view[w].set_sensitive(not new)
            for widget in self.widgets_cancel:
                self.view[widget].set_sensitive(new)
            if not new and self.scan_cd:
                self.scan_cd = False
                # umount/eject cd
                ejectapp = self.model.config.confd['ejectapp']
                if self.model.config.confd['eject'] and ejectapp:
                    msg = deviceHelper.eject_cd(ejectapp,
                                                self.model.config.confd['cd'])
                    if msg != 'ok':
                        Dialogs.Wrn("error ejecting device - pyGTKtalog",
                                    "Cannot eject device pointed to %s" %
                                    self.model.config.confd['cd'],
                                    "Last eject message:\n%s" % msg)
                else:
                    msg = deviceHelper.volumount(self.model.config.confd['cd'])
                    if msg != 'ok':
                        Dialogs.Wrn("error unmounting device - pyGTKtalog",
                                    "Cannot unmount device pointed to %s" %
                                    self.model.config.confd['cd'],
                                    "Last umount message:\n%s" % msg)
        return

    def property_progress_value_change(self, model, old, new):
        self.view['progressbar1'].set_fraction(new)
        return

    #########################
    # private class functions
    def __set_files_hiden_columns_visible(self, boolean):
        """switch visibility of default hidden columns in files treeview"""
        self.view['files'].get_column(0).set_visible(boolean)
        self.view['files'].get_column(2).set_visible(boolean)

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

    def __get_tv_id_under_cursor(self, treeview):
        """get id of item form tree view under cursor"""
        path, column = treeview.get_cursor()
        if path and column:
            model = treeview.get_model()
            tm_iter = model.get_iter(path)
            item_id = model.get_value(tm_iter, 0)
            return item_id
        return None

    def __setup_disc_treeview(self):
        """Setup TreeView discs widget as tree."""
        self.view['discs'].set_model(self.model.discs_tree)

        c = gtk.TreeViewColumn('Filename')

        # one row contains image and text
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        c.pack_start(cellpb, False)
        c.pack_start(cell, True)
        c.set_attributes(cellpb, stock_id=2)
        c.set_attributes(cell, text=1)

        self.view['discs'].append_column(c)

        # registration of treeview signals:

        return

    def __setup_iconview(self):
        """Setup IconView images widget."""
        self.view['images'].set_model(self.model.images_store)
        self.view['images'].set_pixbuf_column(1)
        self.view['images'].set_selection_mode(gtk.SELECTION_MULTIPLE)
        return

    def __setup_files_treeview(self):
        """Setup TreeView files widget, as columned list."""
        v = self.view['files']
        v.set_model(self.model.files_list)

        v.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        c = gtk.TreeViewColumn('Disc', gtk.CellRendererText(), text=1)
        c.set_sort_column_id(1)
        c.set_resizable(True)
        c.set_visible(False)
        self.view['files'].append_column(c)

        c = gtk.TreeViewColumn('Filename')
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        c.pack_start(cellpb, False)
        c.pack_start(cell, True)
        c.set_attributes(cellpb, stock_id=7)
        c.set_attributes(cell, text=2)
        c.set_sort_column_id(2)
        c.set_resizable(True)
        self.view['files'].append_column(c)

        c = gtk.TreeViewColumn('Path', gtk.CellRendererText(), text=3)
        c.set_sort_column_id(3)
        c.set_resizable(True)
        c.set_visible(False)
        self.view['files'].append_column(c)

        c = gtk.TreeViewColumn('Size', gtk.CellRendererText(), text=4)
        c.set_sort_column_id(4)
        c.set_resizable(True)
        self.view['files'].append_column(c)

        c = gtk.TreeViewColumn('Date', gtk.CellRendererText(), text=5)
        c.set_sort_column_id(5)
        c.set_resizable(True)
        self.view['files'].append_column(c)
        self.view['files'].set_search_column(2)

        #v.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
        #                           self.DND_TARGETS,
        #                           gtk.gdk.ACTION_DEFAULT)
        v.drag_source_set(gtk.gdk.BUTTON1_MASK, self.DND_TARGETS,
                          gtk.gdk.ACTION_COPY)
        return

    def __setup_exif_treeview(self):
        self.view['exif_tree'].set_model(self.model.exif_list)

        c = gtk.TreeViewColumn('EXIF key', gtk.CellRendererText(), text=0)
        c.set_sort_column_id(0)
        c.set_resizable(True)
        self.view['exif_tree'].append_column(c)

        c = gtk.TreeViewColumn('EXIF value', gtk.CellRendererText(), text=1)
        c.set_sort_column_id(1)
        c.set_resizable(True)
        self.view['exif_tree'].append_column(c)
        return

    def __activate_ui(self, name=None):
        """Make UI active, and set title"""
        self.model.unsaved_project = False
        self.__set_title(filepath=name)
        return

    def __set_title(self, filepath=None, modified=False):
        """Set main window title"""
        if modified:
            mod = " *"
        else:
            mod = ""

        if filepath:
            self.view['main'].set_title("%s - pyGTKtalog%s" %
                                        (os.path.basename(filepath), mod))
        else:
            self.view['main'].set_title("untitled - pyGTKtalog%s" % mod)
        return

    def __store_settings(self):
        """Store window size and pane position in config file (using config
       object from model)"""
        if self.model.config.confd['savewin']:
            self.model.config.confd['wx'], self.model.config.confd['wy'] = \
            self.view['main'].get_size()
        if self.model.config.confd['savepan']:
            self.model.config.confd['h'] = self.view['hpaned1'].get_position()
            self.model.config.confd['v'] = self.view['vpaned1'].get_position()
        self.model.config.save()
        return

    def __popup_menu(self, event, menu='discs_popup'):
        """Popoup desired menu"""
        self.view[menu].popup(None, None, None, 0, 0)
        #self.view[menu].popup(None, None, None, event.button,
        #                               event.time)
        self.view[menu].show_all()
        return

    def __generate_recent_menu(self):
        self.recent_menu = gtk.Menu()
        for i in self.model.config.recent:
            name = os.path.basename(i)
            item = gtk.MenuItem("%s" % name.replace('_', '__'))
            item.connect_object("activate", self.recent_item_response, i)
            self.recent_menu.append(item)
            item.show()
        self.view['recent_files1'].set_submenu(self.recent_menu)
        return

    def __get_item_info(self, file_id):
        """Get item under cusor, fetch information from model and depending on
        what kind of information file has display it"""
        buf = gtk.TextBuffer()
        if not file_id:
            self.__hide_details()
            return
        #self.view['description'].show()
        set = self.model.get_file_info(file_id)

        tag = buf.create_tag()
        tag.set_property('weight', pango.WEIGHT_BOLD)

        if __debug__ and 'fileinfo' in set:
            buf.insert_with_tags(buf.get_end_iter(), "ID: ", tag)
            buf.insert(buf.get_end_iter(), str(set['fileinfo']['id']) + "\n")
            buf.insert_with_tags(buf.get_end_iter(), "Type: ", tag)
            buf.insert(buf.get_end_iter(), str(set['fileinfo']['type']) + "\n")

        if set['fileinfo']['disc']:
            buf.insert_with_tags(buf.get_end_iter(), "Disc: ", tag)
            buf.insert(buf.get_end_iter(), set['fileinfo']['disc'] + "\n")
        if set['fileinfo']['disc'] and set['fileinfo']['type'] == 1:
            buf.insert_with_tags(buf.get_end_iter(), "Directory: ", tag)
        elif not set['fileinfo']['disc'] and set['fileinfo']['type'] == 1:
            buf.insert_with_tags(buf.get_end_iter(), "Disc: ", tag)
        else:
            buf.insert_with_tags(buf.get_end_iter(), "Filename: ", tag)
        buf.insert(buf.get_end_iter(), set['filename'] + "\n")
        buf.insert_with_tags(buf.get_end_iter(), "Date: ", tag)
        buf.insert(buf.get_end_iter(), str(set['fileinfo']['date']) + "\n")
        buf.insert_with_tags(buf.get_end_iter(), "Size: ", tag)
        buf.insert(buf.get_end_iter(), str(set['fileinfo']['size']) + "\n")

        if 'gthumb' in set:
            tag = buf.create_tag()
            tag.set_property('weight', pango.WEIGHT_BOLD)
            buf.insert_with_tags(buf.get_end_iter(), "\ngThumb comment:\n", tag)
            if set['gthumb']['note']:
                buf.insert(buf.get_end_iter(), set['gthumb']['note'] + "\n")
            if set['gthumb']['place']:
                buf.insert(buf.get_end_iter(), set['gthumb']['place'] + "\n")
            if set['gthumb']['date']:
                buf.insert(buf.get_end_iter(), set['gthumb']['date'] + "\n")

        if 'description' in set:
            tag = buf.create_tag()
            tag.set_property('weight', pango.WEIGHT_BOLD)
            buf.insert_with_tags(buf.get_end_iter(), "\nDetails:\n", tag)
            buf.insert(buf.get_end_iter(), set['description'] + "\n")

        if 'note' in set:
            tag = buf.create_tag()
            tag.set_property('weight', pango.WEIGHT_BOLD)
            buf.insert_with_tags(buf.get_end_iter(), "\nNote:\n", tag)
            buf.insert(buf.get_end_iter(), set['note'] + "\n")

        tags = self.model.get_file_tags(file_id)
        if tags:
            tag = buf.create_tag()
            tag.set_property('weight', pango.WEIGHT_BOLD)
            buf.insert_with_tags(buf.get_end_iter(), "\nFile tags:\n", tag)
            tags = tags.values()
            tags.sort()
            first = True
            for tag in tags:
                if first:
                    first = False
                    buf.insert(buf.get_end_iter(), tag)
                else:
                    buf.insert(buf.get_end_iter(), ", " + tag)

        self.view['description'].set_buffer(buf)

        if 'images' in set:
            self.__setup_iconview()
            self.view['img_container'].show()
        else:
            self.view['img_container'].hide()

        if 'exif' in set:
            self.view['exif_tree'].set_model(self.model.exif_list)
            self.view['exifinfo'].show()
        else:
            self.view['exifinfo'].hide()

        if 'thumbnail' in set:
            self.view['thumb'].set_from_file(set['thumbnail'])
            self.view['thumb_box'].show()
        else:
            self.view['thumb_box'].hide()
        return

    def __tag_cloud(self):
        """generate tag cloud"""
        tag_cloud = self.view['tag_cloud_textview']
        self.model.get_tags()

        def insert_blank(buff, b_iter):
            if b_iter.is_end() and b_iter.is_start():
                return b_iter
            else:
                buff.insert(b_iter, " ")
                b_iter = buff.get_end_iter()
            return b_iter

        buff = tag_cloud.get_buffer()

        # NOTE: remove old tags
        def foreach_rem(texttag, data):
            """remove old tags"""
            tag_table.remove(texttag)

        tag_table = buff.get_tag_table()
        while tag_table.get_size() > 0:
            tag_table.foreach(foreach_rem, None)

        buff.set_text('')

        if len(self.model.tag_cloud) > 0:
            for cloud in self.model.tag_cloud:
                buff_iter = insert_blank(buff, buff.get_end_iter())
                try:
                    tag = buff.create_tag(str(cloud['id']))
                    tag.set_property('size-points', cloud['size'])
                    #tag.connect('event', self.on_tag_cloud_click, tag)
                    tag_repr = cloud['name'] + "(%d)" % cloud['count']
                    buff.insert_with_tags(buff_iter, tag_repr, tag)
                except:
                    if __debug__:
                        print "c_main.py: __tag_cloud: error on tag:", cloud

    def __hide_details(self):
        """hide details and "reset" tabs visibility"""
        buf = self.view['description'].get_buffer()
        buf.set_text('')
        self.view['img_container'].hide()
        self.view['exifinfo'].hide()
        self.view['thumb_box'].hide()
        self.view['description'].set_buffer(buf)

    pass # end of class
