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

import gtk
import pygtk
pygtk.require("2.0")

import gtkmvc
gtkmvc.require("1.2.2")

from src.lib.globs import TOPDIR
from src.lib.globs import APPL_SHORT_NAME
sys.path = [os.path.join(TOPDIR, "src")] + sys.path
from models.m_config import ConfigModel
from models.m_main import MainModel
from ctrls.c_main import MainController
from views.v_main import MainView

def check_requirements():
    """Checks versions and other requirements"""

    conf = ConfigModel()
    conf.load()

    if conf.confd['thumbs'] and conf.confd['retrive']:
        try:
            import Image
        except ImportError:
            print _("WARNING: You'll need Python Imaging Library (PIL), if "
                    "you want to make thumbnails!")
            raise
    return

def run():
    """Create model, controller and view and launch it."""
    # Directory from where pygtkatalog was invoced. We need it for calculate
    # path for argument (catalog file)
    execution_dir = os.path.abspath(os.path.curdir)
    
    # Directory, where this files lies. We need it to setup private source
    # paths
    libraries_dir = os.path.dirname(__file__)
    if libraries_dir:
        os.chdir(libraries_dir)

    # Setup i18n
    locale.setlocale(locale.LC_ALL, '')
    gettext.install(APPL_SHORT_NAME, 'locale', unicode=True)

    check_requirements()

    model = MainModel()
    if len(sys.argv) > 1:
        model.open(os.path.join(execution_dir, sys.argv[1]))
    controler = MainController(model)
    view = MainView(controler)

    try:
        gtk.main()
    except KeyboardInterrupt:
        model.config.save()
        model.cleanup()
        gtk.main_quit

if __name__ == "__main__":
    run()
