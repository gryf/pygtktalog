"""
    Project: pyGTKtalog
    Description: Model for main application
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
from gtkmvc import Model

from pygtktalog.dbobjects import File, Exif, Group, Gthumb
from pygtktalog.dbobjects import Image, Tag, Thumbnail
from pygtktalog.dbcommon import connect, Meta


class MainModel(Model):
    status_bar_message = _("Idle")

    __observables__ = ("status_bar_message",)
