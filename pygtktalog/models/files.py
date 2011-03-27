"""
    Project: pyGTKtalog
    Description: Model for files representation
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2010-11-12
"""
import gtk
import gobject

from gtkmvc import Model

from pygtktalog.dbcommon import Session
from pygtktalog.logger import get_logger

LOG = get_logger("files model")


class FilesModel(Model):
    """
    Model for files representation
    """

    def __init__(self):
        """
        Initialization. Make some nice defaults.
        """
        Model.__init__(self)
        self.files = gtk.ListStore(gobject.TYPE_PYOBJECT,
                                   gobject.TYPE_STRING,
                                   gobject.TYPE_STRING,
                                   gobject.TYPE_STRING,
                                   gobject.TYPE_UINT64,
                                   gobject.TYPE_STRING,
                                   gobject.TYPE_INT,
                                   str)
        self.discs_model = None

    def clear(self):
        """
        Cleanup ListStore model
        """
        self.files.clear()

    def refresh(self, fileob):
        """
        Update files ListStore
        Arguments:
            fileob - File object
        """
        LOG.info("found %d files for File object: %s" % (len(fileob.children),
                                                        str(fileob)))
        self.files.clear()

        for child in fileob.children:
            myiter = self.files.insert_before(None, None)
            self.files.set_value(myiter, 0, child)
            self.files.set_value(myiter, 1, child.parent_id \
                    if child.parent_id != 1 else None)
            self.files.set_value(myiter, 2, child.filename)
            self.files.set_value(myiter, 3, child.filepath)
            self.files.set_value(myiter, 4, child.size)
            self.files.set_value(myiter, 5, child.date)
            self.files.set_value(myiter, 6, 1)
            self.files.set_value(myiter, 7, gtk.STOCK_DIRECTORY \
                    if child.type == 1 else gtk.STOCK_FILE)

    def get_value(self, row=None, fiter=None, column=0):
        """
        TODO:
        """
        if row:
            fiter = self.files.get_iter(row)
        if not fiter:
            LOG.error("ERROR: there is no way to determine gtk_iter object!"
                      " Please specify valid row or gtk_iter!")
            return None

        return self.files.get_value(fiter, column)
