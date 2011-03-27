"""
    Project: pyGTKtalog
    Description: Model for discs representation
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
import gtk
import gobject

from gtkmvc import Model

from pygtktalog.dbobjects import File
from pygtktalog.dbcommon import Session
from pygtktalog.logger import get_logger

LOG = get_logger("discs model")


class DiscsModel(Model):
    """
    Model for discs representation.
    """

    currentdir = None

    __observables__ = ("currentdir",)

    def __init__(self):
        """
        Initialization. Make some nice defaults.
        """
        Model.__init__(self)
        self.discs = gtk.TreeStore(gobject.TYPE_PYOBJECT,
                                   gobject.TYPE_STRING,
                                   str)
        self.files_model = None

    def clear(self):
        """
        Make TreeStore empty
        """
        self.discs.clear()

    def refresh(self, session=Session()):
        """
        Read objects from database, fill TreeStore model with discs
        information
        Arguments:
            @session current sqlalchemy.orm.session.Session object
        """
        LOG.debug("session obj: %s" % str(session))
        dirs = session.query(File).filter(File.type == 1)
        dirs = dirs.order_by(File.filename).all()

        def get_children(parent_id=1, iterator=None):
            """
            Get all children of the selected parent.
            Arguments:
                @parent_id - integer with id of the parent (from db)
                @iterator - gtk.TreeIter, which points to a path inside model
            """
            for fileob in dirs:
                if fileob.parent_id == parent_id:
                    myiter = self.discs.insert_before(iterator, None)
                    self.discs.set_value(myiter, 0, fileob)
                    self.discs.set_value(myiter, 1, fileob.filename)
                    if iterator is None:
                        self.discs.set_value(myiter, 2, gtk.STOCK_CDROM)
                    else:
                        self.discs.set_value(myiter, 2, gtk.STOCK_DIRECTORY)
                    get_children(fileob.id, myiter)
            return
        get_children()
        return True

    def find_path(self, obj):
        """
        Return path of specified File object (which should be the first one)
        """
        path = None
        gtkiter = self.discs.get_iter_first()

        def get_children(iterator):
            """
            Iterate through entire TreeModel, and return path for specified in
            outter scope File object
            """
            if self.discs.get_value(iterator, 0) == obj:
                return self.discs.get_path(iterator)

            if self.discs.iter_has_child(iterator):
                path = get_children(self.discs.iter_children(iterator))
                if path:
                    return path

            iterator = self.discs.iter_next(iterator)
            if iterator is None:
                return None

            return get_children(iterator)

        path = get_children(gtkiter)
        LOG.debug("found path for object '%s': %s" % (str(obj), str(path)))
        return path


