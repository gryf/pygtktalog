# -*- coding: utf-8 -*-

import gtk


class MainWindow(object):
    def __init__(self):
        self.window = gtk.Window()
        self.window.set_title("pygtktalog")
        self.window.connect("delete-event", gtk.main_quit)

        self.recent = None

        box = gtk.VBox(False, 0)

        vpaned = gtk.VPaned()

        menubar = self.get_main_menu()
        box.pack_start(menubar, False, True, 0)

        box.pack_start(vpaned, True, True, 0)

        self.window.add(box)
        self.window.add(vpaned)
        self.window.show_all()

    def menu(self):
        return(gtk.MenuBar())

    def fake_recent(self):
        recent_menu = gtk.Menu()
        for i in "one two techno foo bar baz".split():
            item = gtk.MenuItem(i)
            item.connect_object("activate", self.on_recent_activate,
                                "/some/fake/path/" + i)
            recent_menu.append(item)
            item.show()
        self.recent.set_submenu(recent_menu)

    def get_main_menu(self):
        menu_items = (("/_File", None, None, 0, "<Branch>"),
                      ("/File/_New", "<control>N", self.on_menu_callback,
                       0, '<StockItem>', gtk.STOCK_NEW),
                      ("/File/_Open", "<control>O", self.on_menu_callback,
                       0, '<StockItem>', gtk.STOCK_OPEN),
                      ("/File/_Save", "<control>S", self.on_menu_callback,
                       0, '<StockItem>', gtk.STOCK_SAVE),
                      ("/File/Save _As", None, self.on_menu_callback, 0,
                       '<StockItem>', gtk.STOCK_SAVE_AS),
                      ("/File/sep1", None, None, 0, "<Separator>"),
                      ("/File/Import", None, None, 0, None),
                      ("/File/Export", None, None, 0, None),
                      ("/File/sep2", None, None, 0, "<Separator>"),
                      ("/File/Recent files", None, None, 0, None),
                      ("/File/sep3", None, None, 0, "<Separator>"),
                      ("/File/_Quit", "<control>Q", gtk.main_quit, 0,
                       '<StockItem>', gtk.STOCK_QUIT),
                      ("/_Edit", None, None, 0, "<Branch>"),
                      ("/Edit/_Delete", "Delete", None, 0, '<StockItem>',
                       gtk.STOCK_DELETE),
                      ("/Edit/sep4", None, None, 0, "<Separator>"),
                      ("/Edit/_Find", "<control>F", None, 0,
                       '<StockItem>', gtk.STOCK_FIND),
                      ("/Edit/sep5", None, None, 0, "<Separator>"),
                      ("/Edit/_Preferences", None, None, 0,
                       '<StockItem>', gtk.STOCK_PREFERENCES),
                      ("/_Catalog", None, None, 0, "<Branch>"),
                      ("/Catalog/Add CD\/DVD", "<control>E", None, 0, None),
                      ("/Catalog/Add Directory", "<control>D", None, 0, None),
                      ("/Catalog/sep6", None, None, 0, "<Separator>"),
                      ("/Catalog/Delete all images", None, None, 0, None),
                      ("/Catalog/Delete all thumbnals", None, None, 0, None),
                      ("/Catalog/Save all images…", None, None, 0, None),
                      ("/Catalog/sep7", None, None, 0, "<Separator>"),
                      ("/Catalog/Catalog _statistics", None, None, 0, None),
                      ("/Catalog/sep8", None, None, 0, "<Separator>"),
                      ("/Catalog/Cancel", None, None, 0, '<StockItem>',
                       gtk.STOCK_CANCEL),
                      ("/_View", None, None, 0, "<Branch>"),
                      ("/View/Toolbar", None, None, 0, '<ToggleItem>'),
                      ("/View/Status bar", None, None, 0, '<ToggleItem>'),
                      ("/_Help", None, None, 0, "<LastBranch>"),
                      ("/_Help/About", None, self.on_about_activate, 0,
                       '<StockItem>', gtk.STOCK_ABOUT))

        accel_group = gtk.AccelGroup()
        item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)
        item_factory.create_items(menu_items)

        # get recent menu item, and build recent submenu
        self.recent = item_factory.get_item('/File/Recent files')
        self.fake_recent()

        self.menu_cancel = item_factory.get_item('/Catalog/Cancel')
        self.menu_cancel.set_sensitive(False)


        self.window.add_accel_group(accel_group)
        # Finally, return the actual menu bar created by the item factory.
        return item_factory.get_widget("<main>")

    def on_menu_callback(self, *args, **kwargs):
        return

    def on_about_activate(self, event, menuitem):
        print "about", event, menuitem
        return

    def on_recent_activate(self, *args, **kwargs):
        print args, kwargs


def run():
    gui = MainWindow()
    gtk.mainloop()
