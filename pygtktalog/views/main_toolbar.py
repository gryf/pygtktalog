"""
Project: pyGTKtalog
Description: Toolbar for the main window
Type: interface
Author: Roman 'gryf' Dobosz, gryf73@gmail.com
Created: 2010-04-20 18:47:49
"""

import gtk

from gtkmvc import View


class ToolBar(View):
    def __init__(self):
        View.__init__(self)
        self['maintoolbar'] = gtk.Toolbar()

