#!/usr/bin/env python
"""
    Project: pyGTKtalog
    Description: Application main launch file.
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2007-05-01
"""
import sys

import gtk
import pygtk
pygtk.require("2.0")

import gtkmvc
gtkmvc.require("1.99.0")

from pygtktalog.models.main import MainModel
from pygtktalog.controllers.main import MainController
from pygtktalog.views.main import MainView
from pygtktalog.logger import get_logger


LOG = get_logger('__main__')


def run(*args):
    """Create model, controller and view and launch it."""
    model = MainModel()
    if args:
        LOG.info("args %s", str(args))
        if not model.open(args[0][1]):
            LOG.warn("file couldn't be open")
            sys.exit()
    #else:
    #    model.new()
    view = MainView()
    MainController(model, view)

    try:
        gtk.main()
    except KeyboardInterrupt:
        #model.config.save()
        LOG.exception("gtktalog.py: model.cleanup()")
        model.cleanup()
        gtk.main_quit


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(sys.argv)
    else:
        run()

