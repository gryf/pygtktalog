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
import gobject
import os
import utils.globals

class Qst(object):
    """Show simple dialog for questions
        if "OK" button pressed, return "True"
        "Cancel" button return "False"
    """

    def __init__(self, title="", message="", secondarymsg=""):
        self.dialog = gtk.MessageDialog(
            flags = gtk.DIALOG_DESTROY_WITH_PARENT,
            type = gtk.MESSAGE_QUESTION,
            buttons = gtk.BUTTONS_OK_CANCEL,
            message_format = message,
        )
        self.dialog.set_title(title)
        self.dialog.format_secondary_text(secondarymsg)

    def run(self):
        retval = self.dialog.run()
        retval = False
        if retval == gtk.RESPONSE_OK:
            retval = True
        self.dialog.destroy()
        return retval

class Inf(object):
    """Show simple dialog for notices"""

    def __init__(self, title="", message="", secondarymsg=""):
        self.dialog = gtk.MessageDialog(
            flags = gtk.DIALOG_DESTROY_WITH_PARENT,
            type = gtk.MESSAGE_INFO,
            buttons = gtk.BUTTONS_OK,
            message_format = message,
        )
        self.dialog.set_title(title)
        self.dialog.format_secondary_text(secondarymsg)
        self.dialog.connect('response',
                            lambda dialog, response: self.ret(response))
        self.dialog.show()

    def ret(self,result):
        self.dialog.destroy()
        return True

class Wrn(object):
    """Show simple dialog for warnings"""

    def __init__(self, title="", message="", secondarymsg=""):
        self.dialog = gtk.MessageDialog(
            flags = gtk.DIALOG_DESTROY_WITH_PARENT,
            type = gtk.MESSAGE_WARNING,
            buttons = gtk.BUTTONS_CLOSE,
            message_format = message,
        )
        self.dialog.set_title(title)
        self.dialog.format_secondary_text(secondarymsg)
        self.dialog.connect('response',
                            lambda dialog, response: self.ret(response))
        self.dialog.show()

    def ret(self,result):
        self.dialog.destroy()
        return True

class Err(object):
    """Show simple dialog for errors"""

    def __init__(self, title="", message="", secondarymsg=""):
        self.dialog = gtk.MessageDialog(
            flags = gtk.DIALOG_DESTROY_WITH_PARENT,
            type = gtk.MESSAGE_ERROR,
            buttons = gtk.BUTTONS_CLOSE,
            message_format = message)

        self.dialog.set_title(title)
        self.dialog.format_secondary_text(secondarymsg)
        self.dialog.connect('response',
                            lambda dialog, response: self.ret(response))
        self.dialog.run()

    def ret(self,result):
        self.dialog.destroy()
        return True

class Abt(object):
    """Show simple about dialog"""

    def __init__(self, name=None, ver="", title="", authors=[],licence=""):
        self.dialog = gtk.AboutDialog()
        self.dialog.set_title(title)
        self.dialog.set_version(ver)
        self.dialog.set_license(licence)
        self.dialog.set_name(name)
        self.dialog.set_authors(authors)
        self.dialog.connect('response',
                            lambda dialog, response: self.dialog.destroy())
        self.dialog.show()

class InputDiskLabel(object):
    """Sepcific dialog for quering user for a disc label"""

    def __init__(self, label=""):
        self.gladefile = os.path.join(utils.globals.GLADE_DIR, "dialogs.glade")
        self.label = ""
        if label!= None:
            self.label = label

    def run(self):
        gladexml = gtk.glade.XML(self.gladefile, "inputDialog")
        dialog = gladexml.get_widget("inputDialog")
        entry = gladexml.get_widget("volname")
        entry.set_text(self.label)
        result = dialog.run()
        res = None
        if result == gtk.RESPONSE_OK:
            res = entry.get_text()
        dialog.destroy()
        return res

class InputNewName(object):
    """Sepcific dialog for quering user for a disc label"""

    def __init__(self, name=""):
        self.gladefile = os.path.join(utils.globals.GLADE_DIR, "dialogs.glade")
        self.label = ""
        self.name = name

    def run(self):
        gladexml = gtk.glade.XML(self.gladefile, "renameDialog")
        dialog = gladexml.get_widget("renameDialog")
        entry = gladexml.get_widget("name")
        entry.set_text(self.name)
        result = dialog.run()
        res = None
        if result == gtk.RESPONSE_OK:
            res = entry.get_text()
        dialog.destroy()
        return res

class PointDirectoryToAdd(object):
    """Sepcific dialog for quering user for selecting directory to add"""

    URI="file://"+os.path.abspath(os.path.curdir)

    def __init__(self,volname='',dirname=''):
        self.gladefile = os.path.join(utils.globals.GLADE_DIR, "dialogs.glade")
        self.gladexml = gtk.glade.XML(self.gladefile, "addDirDialog")
        self.volname = self.gladexml.get_widget("dirvolname")
        self.volname.set_text(volname)
        self.directory = self.gladexml.get_widget("directory")
        self.directory.set_text(dirname)
        sigs = {"on_browse_activate":self.show_dirchooser,
                "on_browse_clicked":self.show_dirchooser}
        self.gladexml.signal_autoconnect(sigs)

    def show_dirchooser(self,widget):
        """dialog for point the mountpoint"""
        dialog = gtk.FileChooserDialog(
            title="Choose directory to add",
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK))

        dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        dialog.set_default_response(gtk.RESPONSE_OK)

        if self.URI:
            dialog.set_current_folder_uri(self.URI)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.directory.set_text(dialog.get_filename())
            self.__class__.URI = dialog.get_current_folder_uri()
        dialog.destroy()

    def run(self):
        dialog = self.gladexml.get_widget("addDirDialog")
        ch = True
        result = dialog.run()
        while ch:
            if result == gtk.RESPONSE_OK and (self.volname.get_text() == '' or \
                                              self.directory.get_text() == ''):
                a = Err("Error - pyGTKtalog",
                        "There are fields needed to be filled.",
                        "Cannot add directory without path and disc label.")
                ch = True
                result = dialog.run()
            else:
                ch = False

        volname = self.volname.get_text()
        directory = self.directory.get_text()

        res = (None,None)
        if result == gtk.RESPONSE_OK:
            res = (volname, directory)
        dialog.destroy()
        return res

class SelectDirectory(object):
    """Sepcific dialog for quering user for selecting directory to add"""

    URI="file://"+os.path.abspath(os.path.curdir)

    def __init__(self, title=None):
        if title:
            self.title = title
        else:
            self.title = "Choose directory"

    def run(self):
        """dialog for point the mountpoint"""
        dialog = gtk.FileChooserDialog(
            title = self.title,
            action = gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons = (
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK))

        dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        dialog.set_default_response(gtk.RESPONSE_OK)

        retval = None

        if self.URI:
            dialog.set_current_folder_uri(self.URI)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            retval = dialog.get_filename()
            self.__class__.URI = dialog.get_current_folder_uri()
        dialog.destroy()
        return retval

class ChooseFilename(object):
    """Dialog for quering user for selecting filename"""

    URI=None

    def __init__(self, path=None, title=''):
        self.path = path
        self.dialog = gtk.FileChooserDialog(
            title="",
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE,
                gtk.RESPONSE_OK))

        self.dialog.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        self.dialog.set_default_response(gtk.RESPONSE_OK)
        self.dialog.set_do_overwrite_confirmation(True)
        self.dialog.set_title(title)

        f = gtk.FileFilter()
        f.set_name("Catalog files")
        f.add_pattern("*.sqlite")
        f.add_pattern("*.sqlite.bz2")
        self.dialog.add_filter(f)
        f = gtk.FileFilter()
        f.set_name("All files")
        f.add_pattern("*.*")
        self.dialog.add_filter(f)

    def run(self):
        if self.URI:
            self.dialog.set_current_folder_uri(self.URI)
        elif self.path and os.path.exists(self.path):
            self.path = "file://"+os.path.abspath(self.path)
            self.dialog.set_current_folder_uri(self.path)

        response = self.dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = self.dialog.get_filename()
            self.__class__.URI = self.dialog.get_current_folder_uri()
            self.dialog.destroy()
            return filename
        else:
            self.dialog.destroy()
            return None
    pass

class ChooseDBFilename(ChooseFilename):
    """Sepcific dialog for quering user for selecting filename for database"""

    URI=None

    def __init__(self, path=None):
        ChooseFilename.__init__(self)
        self.dialog.set_title('Save catalog as...')

        f = gtk.FileFilter()
        f.set_name("Catalog files")
        f.add_pattern("*.sqlite")
        f.add_pattern("*.sqlite.bz2")
        self.dialog.add_filter(f)
        f = gtk.FileFilter()
        f.set_name("All files")
        f.add_pattern("*.*")
        self.dialog.add_filter(f)

    def run(self):
        if self.URI:
            self.dialog.set_current_folder_uri(self.URI)
        elif self.path and os.path.exists(self.path):
            self.path = "file://"+os.path.abspath(self.path)
            self.dialog.set_current_folder_uri(self.path)

        response = self.dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = self.dialog.get_filename()
            self.__class__.URI = self.dialog.get_current_folder_uri()
            self.dialog.destroy()
            return filename
        else:
            self.dialog.destroy()
            return None
    pass

class LoadDBFile(object):
    """Specific class for displaying openFile dialog. It has veryfication
    for file existence."""

    URI = None

    def __init__(self, path=None):
        self.path = path

        self.dialog = gtk.FileChooserDialog(
            title="Open catalog",
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK))

        self.dialog.set_default_response(gtk.RESPONSE_OK)

        f = gtk.FileFilter()
        f.set_name("Catalog files")
        f.add_pattern("*.sqlite")
        f.add_pattern("*.sqlite.bz2")
        self.dialog.add_filter(f)
        f = gtk.FileFilter()
        f.set_name("All files")
        f.add_pattern("*.*")
        self.dialog.add_filter(f)

    def show_dialog(self):
        response = self.dialog.run()
        filename = None
        if response == gtk.RESPONSE_OK:
            try:
                filename = self.dialog.get_filename()
            except:
                pass
            #self.dialog.destroy()
            return 'ok',filename
        else:
            return 'cancel',None

    def run(self):
        if self.URI:
            self.dialog.set_current_folder_uri(self.URI)
        elif self.path and os.path.exists(self.path):
            self.path = "file://"+os.path.abspath(self.path)
            self.dialog.set_current_folder_uri(self.path)

        res,filename = self.show_dialog()
        ch = True
        while ch:
            if res == 'cancel':
                self.dialog.destroy()
                return None
            try:
                os.stat(filename)
                self.__class__.URI = self.dialog.get_current_folder_uri()
                self.dialog.destroy()
                return filename
            except:
                a = Err("Error - pyGTKtalog","File doesn't exist.",
                        "The file that you choose does not exist." + \
                        " Choose another one, or cancel operation.")
                ch = True
                res, filename = self.show_dialog()


class LoadImageFile(object):
    """class for displaying openFile dialog. It have possibility of multiple
    selection."""

    URI="file://"+os.path.abspath(os.path.curdir)

    def __init__(self, multiple=False):
        self.dialog = gtk.FileChooserDialog(
            title="Select image",
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK))
        self.dialog.set_select_multiple(multiple)
        self.dialog.set_default_response(gtk.RESPONSE_OK)

        f = gtk.FileFilter()
        f.set_name("All Images")
        for i in ['*.jpg', '*.jpeg', '*.gif', '*.png', '*.tif', '*.tiff',
                  '*.tga', '*.pcx', '*.bmp', '*.xbm', '*.xpm', '*.jp2',
                  '*.jpx', '*.pnm', '*.JPG', '*.JPEG', '*.GIF', '*.PNG',
                  '*.TIF', '*.TIFF', '*.TGA', '*.PCX', '*.BMP', '*.XBM',
                  '*.XPM', '*.JP2', '*.JPX', '*.PNM']:
            f.add_pattern(i)
        self.dialog.add_filter(f)
        f = gtk.FileFilter()
        f.set_name("All files")
        f.add_pattern("*.*")
        self.dialog.add_filter(f)
        self.preview = gtk.Image()

        self.dialog.set_preview_widget(self.preview)
        self.dialog.connect("update-preview", self.update_preview_cb)

    def run(self):
        if self.URI:
            self.dialog.set_current_folder_uri(self.URI)
        response = self.dialog.run()
        filenames = None
        only_thumbs = False

        if response == gtk.RESPONSE_OK:
            try:
                if self.dialog.get_select_multiple():
                    filenames = self.dialog.get_filenames()
                else:
                    filenames = self.dialog.get_filename()

                if self.dialog.get_extra_widget().get_active():
                    only_thumbs = True
            except:
                pass

        self.__class__.URI = self.dialog.get_current_folder_uri()
        self.dialog.destroy()
        return filenames, only_thumbs

    def update_preview_cb(self, widget):
        filename = self.dialog.get_preview_filename()
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 128, 128)
            self.preview.set_from_pixbuf(pixbuf)
            have_preview = True
        except:
            have_preview = False
        self.dialog.set_preview_widget_active(have_preview)
        return

class StatsDialog(object):
    """Sepcific dialog for display stats"""

    def __init__(self, values={}):
        self.gladefile = os.path.join(utils.globals.GLADE_DIR, "dialogs.glade")
        self.values = values

    def run(self):
        gladexml = gtk.glade.XML(self.gladefile, "statDialog")
        dialog = gladexml.get_widget("statDialog")

        if 'discs' in self.values:
            entry = gladexml.get_widget("discs_entry")
            entry.set_text(str(self.values['discs']))
        else:
            label = gladexml.get_widget("discs_label")
            entry = gladexml.get_widget("discs_entry")
            label.hide()
            entry.hide()

        if 'dirs' in self.values:
            entry = gladexml.get_widget("dirs_entry")
            entry.set_text(str(self.values['dirs']))
        else:
            label = gladexml.get_widget("dirs_label")
            entry = gladexml.get_widget("dirs_entry")
            label.hide()
            entry.hide()

        if 'files' in self.values:
            entry = gladexml.get_widget("files_entry")
            entry.set_text(str(self.values['files']))

        if 'size' in self.values:
            entry = gladexml.get_widget("size_entry")
            entry.set_text(str(self.values['size']))

        result = dialog.run()
        retval = None
        if result == gtk.RESPONSE_OK:
            retval = entry.get_text()
        dialog.destroy()
        return retval

class TagsDialog(object):
    """Sepcific dialog for display stats"""

    def __init__(self):
        self.gladefile = os.path.join(utils.globals.GLADE_DIR, "dialogs.glade")

    def run(self):
        gladexml = gtk.glade.XML(self.gladefile, "tagsDialog")
        dialog = gladexml.get_widget("tagsDialog")

        entry = gladexml.get_widget("tag_entry1")

        result = dialog.run()

        retval = None
        if result == gtk.RESPONSE_OK:
            retval = entry.get_text()
        dialog.destroy()
        return retval

class TagsRemoveDialog(object):
    """Sepcific dialog for display stats"""

    def __init__(self, tag_dict=None):
        self.gladefile = os.path.join(utils.globals.GLADE_DIR, "dialogs.glade")
        self.tag_dict = tag_dict

    def run(self):
        if not self.tag_dict:
            return None

        gladexml = gtk.glade.XML(self.gladefile, "tagRemove")
        dialog = gladexml.get_widget("tagRemove")

        # declare model
        model = gtk.ListStore(gobject.TYPE_INT,
                              gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
        # sort dict
        values = self.tag_dict.values()
        values.sort()
        keys = []
        for val in values:
            for d_key, d_value in self.tag_dict.items():
                if d_value == val:
                    keys.append(d_key)

        # fill model with dict
        for count in range(len(keys)):
            myiter = model.insert_before(None, None)
            model.set_value(myiter, 0, keys[count])
            model.set_value(myiter, 1, values[count])
            model.set_value(myiter, 2, None)

        def toggle(cell, path, model):
            model[path][2] = not model[path][2]

        def toggle_all(column, model):
            for row in model:
                row[2] = not row[2]

        treeview = gladexml.get_widget("treeview1")
        treeview.set_model(model)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Tag", renderer, text=1)
        column.set_property('expand', True)
        treeview.append_column(column)

        renderer = gtk.CellRendererToggle()
        renderer.set_property('activatable', True)
        renderer.connect('toggled', toggle, model)
        column = gtk.TreeViewColumn("Toggle", renderer)
        column.add_attribute(renderer, "active", 2)
        column.set_property('expand', False)
        column.set_property("clickable", True)
        column.connect("clicked", toggle_all, model)
        treeview.append_column(column)

        result = dialog.run()

        retval = (None, None)
        if result == gtk.RESPONSE_OK:
            ids = []
            for i in model:
                if i[2]:
                    ids.append(i[0])
            retval = ("ok", ids)
        dialog.destroy()
        return retval

class EditDialog(object):
    """Sepcific dialog for display stats"""

    def __init__(self, values={}):
        self.gladefile = os.path.join(utils.globals.GLADE_DIR, "dialogs.glade")
        self.values = values

    def run(self):
        gladexml = gtk.glade.XML(self.gladefile, "file_editDialog")
        dialog = gladexml.get_widget("file_editDialog")

        filename = gladexml.get_widget("filename_entry")
        filename.set_text(str(self.values['filename']))
        description = gladexml.get_widget("description_text")
        note = gladexml.get_widget("note_text")

        if 'description' in self.values:
            buff = gtk.TextBuffer()
            buff.set_text(str(self.values['description']))
            description.set_buffer(buff)

        if 'note' in self.values:
            buff = gtk.TextBuffer()
            buff.set_text(str(self.values['note']))
            note.set_buffer(buff)

        result = dialog.run()
        if result == gtk.RESPONSE_OK:
            d = description.get_buffer()
            n = note.get_buffer()
            retval = {'filename': filename.get_text(),
                    'description': d.get_text(d.get_start_iter(),
                                              d.get_end_iter()),
                    'note': n.get_text(n.get_start_iter(), n.get_end_iter())}
            dialog.destroy()
            return retval
        dialog.destroy()
        return None
