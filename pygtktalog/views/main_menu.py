"""
Project: pyGTKtalog
Description: Menu for the main window
Type: interface
Author: Roman 'gryf' Dobosz, gryf73@gmail.com
Created: 2010-03-14 21:31:57
"""

import gtk

from gtkmvc import View


class MainMenu(View):
    def __init__(self):
        View.__init__(self)
        self['mainMenu'] = gtk.MenuBar()

        self['file_menu'] = gtk.MenuItem(_("_File"))

        accel_group = gtk.AccelGroup()
        menu_items = (("/_File", None, None, 0, "<Branch>"),
                      ("/File/_New", "<control>N", None, 0, None),
                      ("/File/_Open", "<control>O", None, 0, None),
                      ("/File/_Save", "<control>S", None, 0, None),
                      ("/File/Save _As", None, None, 0, None),
                      ("/File/sep1", None, None, 0, "<Separator>"),
                      ("/File/Quit", "<control>Q", gtk.main_quit, 0, None),
                      ("/_Options", None, None, 0, "<Branch>"),
                      ("/Options/Test", None, None, 0, None),
                      ("/_Help", None, None, 0, "<LastBranch>"),
                      ("/_Help/About", None, None, 0, None),)
        item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)
        item_factory.create_items(menu_items)


