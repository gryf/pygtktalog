"""
    Project: pyGTKtalog
    Description: Model(s) for details part of the application
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2010-11-09
"""
import gtk
import gobject

from gtkmvc import Model


class DetailsModel(Model):
    """
    Main model for application.
    It is responsible for communicate with database objects and I/O
    operations.
    """

    exif = gtk.ListStore(gobject.TYPE_PYOBJECT,
                                   gobject.TYPE_STRING,
                                   gobject.TYPE_STRING,
                                   gobject.TYPE_STRING,
                                   gobject.TYPE_UINT64,
                                   gobject.TYPE_STRING,
                                   gobject.TYPE_INT,
                                   str)

    __observables__ = ['exif']

