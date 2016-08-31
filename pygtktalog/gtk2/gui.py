# -*- coding: utf-8 -*-

import gtk

from pygtktalog import logger

UI = """
<ui>

<menubar name="MenuBar">
    <menu action="File">
        <menuitem action="New"/>
        <menuitem action="Open"/>
        <menuitem action="Save"/>
        <menuitem action="Save As"/>
        <separator/>
        <menuitem action="Import"/>
        <menuitem action="Export"/>
        <separator/>
        <menuitem action="Recent"/>
        <separator/>
        <menuitem action="Quit"/>
    </menu>
    <menu action="Edit">
        <menuitem action="Delete"/>
        <separator/>
        <menuitem action="Find"/>
        <separator/>
        <menuitem action="Preferences"/>
    </menu>
    <menu action="Catalog">
        <menuitem action="Add_CD"/>
        <menuitem action="Add_Dir"/>
        <separator/>
        <menuitem action="Delete_all_images"/>
        <menuitem action="Delete_all_thumbnails"/>
        <menuitem action="Save_all_images"/>
        <separator/>
        <menuitem action="Catalog_statistics"/>
        <separator/>
        <menuitem action="Cancel"/>
    </menu>
    <menu action="View">
        <menuitem action="Toolbar"/>
        <menuitem action="Statusbar"/>
    </menu>
    <menu action="Help">
        <menuitem action="About"/>
    </menu>
</menubar>

<toolbar name="ToolBar">
    <toolitem action="New"/>
    <toolitem action="Open"/>
    <toolitem action="Save"/>
    <separator/>
    <toolitem action="Add_CD"/>
    <toolitem action="Add_Dir"/>
    <toolitem action="Find"/>
    <separator/>
    <toolitem action="Cancel"/>
    <toolitem action="Quit"/>
    <toolitem action="Debug"/>
</toolbar>

</ui>
"""
LOG = logger.get_logger(__name__)
LOG.setLevel(2)


class ConnectedWidgets(object):
    """grouped widgets"""
    def __init__(self, toolbar, menu):
        super(ConnectedWidgets, self).__init__()
        self.toolbar = toolbar
        self.menu = menu

    def hide(self):
        self.toolbar.hide()
        self.menu.hide()

    def show(self):
        self.toolbar.show()
        self.menu.show()

    def set_sensitive(self, state):
        self.toolbar.set_sensitive(state)
        self.menu.set_sensitive(state)


class MainWindow(object):

    def __init__(self, debug=False):
        """Initialize window"""
        LOG.debug("initialize")
        self.window = gtk.Window()
        self.window.set_default_size(650, -1)
        self.window.set_title("pygtktalog")
        self.window.connect("delete-event", self.on_quit)

        self.recent = None
        self.toolbar = None
        self.statusbar = None
        self.cancel = None
        self.debug = None

        vbox = gtk.VBox(False, 0)

        self._setup_menu_toolbar(vbox)

        # TODO:
        # 1. toolbar with selected tags
        # 2. main view (splitter)
        # 3. treeview with tag cloud (left split)
        # 4. splitter (right split)
        # 5. file list (upper split)
        # 6. details w images and thumb (lower split)
        # 7. status bar (if needed…)

        hbox = gtk.HBox(False, 0)
        vbox.add(hbox)

        self.window.add(vbox)
        self.window.show_all()
        self.debug.hide()

    def fake_recent(self):
        recent_menu = gtk.Menu()
        for i in "one two techno foo bar baz".split():
            item = gtk.MenuItem(i)
            item.connect_object("activate", self.on_recent,
                                "/some/fake/path/" + i)
            recent_menu.append(item)
            item.show()
        self.recent.set_submenu(recent_menu)

    def _setup_menu_toolbar(self, vbox):
        """Create menu/toolbar using uimanager."""
        actions = [('File', None, '_File'),
                   ('New', gtk.STOCK_NEW, '_New', None, 'Create new catalog', self.on_new),
                   ('Open', gtk.STOCK_OPEN, '_Open', None, 'Open catalog file', self.on_open),
                   ('Save', gtk.STOCK_SAVE, '_Save', None, 'Save catalog file', self.on_save),
                   ('Save As', gtk.STOCK_SAVE_AS, '_Save As', None, None, self.on_save),
                   ('Import', None, '_Import', None, None, self.on_import),
                   ('Export', None, '_Export', None, None, self.on_export),
                   ('Recent', None, '_Recent files'),
                   ('Quit', gtk.STOCK_QUIT, '_Quit', None, 'Quit the Program', self.on_quit),
                   ('Edit', None, '_Edit'),
                   ('Delete', gtk.STOCK_DELETE, '_Delete', None, None, self.on_delete),
                   ('Find', gtk.STOCK_FIND, '_Find', None, 'Find file', self.on_find),
                   ('Preferences', gtk.STOCK_PREFERENCES, '_Preferences'),
                   ('Catalog', None, '_Catalog'),
                   ('Add_CD', gtk.STOCK_CDROM, '_Add CD', None, 'Add CD/DVD/BR to catalog'),
                   ('Add_Dir', gtk.STOCK_DIRECTORY, '_Add Dir', None, 'Add directory to catalog'),
                   ('Delete_all_images', None, '_Delete all images'),
                   ('Delete_all_thumbnails', None, '_Delete all thumbnails'),
                   ('Save_all_images', None, '_Save all images…'),
                   ('Catalog_statistics', None, '_Catalog statistics'),
                   ('Cancel', gtk.STOCK_CANCEL, '_Cancel'),
                   ('View', None, '_View'),
                   ('Help', None, '_Help'),
                   ('About', gtk.STOCK_ABOUT, '_About'),
                   ('Debug', gtk.STOCK_DIALOG_INFO, 'Debug')]

        toggles = [('Toolbar', None, '_Toolbar'),
                   ('Statusbar', None, '_Statusbar')]

        mgr = gtk.UIManager()
        accelgrp = mgr.get_accel_group()
        self.window.add_accel_group(accelgrp)

        agrp = gtk.ActionGroup("Actions")
        agrp.add_actions(actions)
        agrp.add_toggle_actions(toggles)

        mgr.insert_action_group(agrp, 0)
        mgr.add_ui_from_string(UI)

        help_widget = mgr.get_widget("/MenuBar/Help")
        help_widget.set_right_justified(True)

        self.recent = mgr.get_widget("/MenuBar/File/Recent")
        self.fake_recent()

        menubar = mgr.get_widget("/MenuBar")
        vbox.pack_start(menubar)
        self.toolbar = mgr.get_widget("/ToolBar")
        vbox.pack_start(self.toolbar)

        menu_cancel = mgr.get_widget('/MenuBar/Catalog/Cancel')
        toolbar_cancel = mgr.get_widget('/ToolBar/Cancel')
        self.cancel = ConnectedWidgets(toolbar_cancel, menu_cancel)
        self.cancel.set_sensitive(False)

        self.debug = mgr.get_widget('/ToolBar/Debug')

        self.toolbar = mgr.get_widget('/MenuBar/View/Toolbar')
        self.statusbar = mgr.get_widget('/MenuBar/View/Statusbar')

    def on_new(self, *args, **kwargs):
        LOG.debug("On new")
        return

    def on_open(self, *args, **kwargs):
        LOG.debug("On open")
        return

    def on_save(self, *args, **kwargs):
        LOG.debug("On save")
        return

    def on_save_as(self, *args, **kwargs):
        LOG.debug("On save as")
        return

    def on_import(self, *args, **kwargs):
        LOG.debug("On import")
        return

    def on_export(self, *args, **kwargs):
        LOG.debug("On export")
        return

    def on_recent(self, *args, **kwargs):
        LOG.debug("On recent")
        print args, kwargs

    def on_quit(self, *args, **kwargs):
        LOG.debug("on quit")
        gtk.main_quit()

    def on_delete(self, *args, **kwargs):
        LOG.debug("On delete")
        return

    def on_find(self, *args, **kwargs):
        LOG.debug("On find")
        return

    def on_about(self, event, menuitem):
        LOG.debug("about", event, menuitem)
        return


def run():
    gui = MainWindow()
    gtk.mainloop()
