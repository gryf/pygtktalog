"""
    Project: pyGTKtalog
    Description: Application main launch file.
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2007-05-01
"""
import sys
import os
import locale
import gettext

import __builtin__

import gtk
import pygtk
pygtk.require("2.0")

import gtkmvc
gtkmvc.require("1.99.0")


# Setup i18n
# adapted from example by Armin Ronacher:
# http://lucumr.pocoo.org/2007/6/10/internationalized-pygtk-applications2
GETTEXT_DOMAIN = 'pygtktalog'
LOCALE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'locale')

locale.setlocale(locale.LC_ALL, '')
for module in gtk.glade, gettext:
    module.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
    module.textdomain(GETTEXT_DOMAIN)

# register the gettext function for the whole interpreter as "_"
__builtin__._ = gettext.gettext


from pygtktalog.models.main import MainModel
from pygtktalog.controllers.main import MainController
from pygtktalog.views.main import MainView

def run():
    """Create model, controller and view and launch it."""
    model = MainModel()
    if len(sys.argv) > 1:
        model.open(os.path.join(execution_dir, sys.argv[1]))
    view = MainView()
    controler = MainController(model, view)

    try:
        gtk.main()
    except KeyboardInterrupt:
        #model.config.save()
        #model.cleanup()
        gtk.main_quit

if __name__ == "__main__":
    run()
