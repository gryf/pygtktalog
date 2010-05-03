"""
    Project: pyGTKtalog
    Description: Model for main application
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
import os
import bz2
from string import printable
from tempfile import mkstemp

import gtk
import gobject
from gtkmvc import ModelMT

from pygtktalog.dbobjects import File, Exif, Group, Gthumb
from pygtktalog.dbobjects import Image, Tag, Thumbnail
from pygtktalog.dbcommon import connect, Meta, Session
from pygtktalog.logger import get_logger

LOG = get_logger("main model")


class MainModel(ModelMT):
    """
    Main model for application.
    It is responsible for communicate with database objects and I/O
    operations.
    """
    status_bar_message = _("Idle")
    current_disc = None

    __observables__ = ("status_bar_message", "current_disc")

    def __init__(self, filename=None):
        """
        Initialization. Make some nice defaults.
        Arguments:
            filename - String that indicates optionally compressed with bzip2
                       file containing sqlite3 database.
        """
        ModelMT.__init__(self)
        # Opened/saved database location in filesystem. Could be compressed.
        self.cat_fname = filename
        # Temporary (usually in /tmp) working database.
        self.tmp_filename = None
        # Flag indicates, that db was compressed
        # TODO: make it depend on configuration
        self.compressed = False

        self.db_unsaved = False

        self.discs = gtk.TreeStore(gobject.TYPE_PYOBJECT,
                                   gobject.TYPE_STRING,
                                   str)

        if self.cat_fname:
            self.open(self.cat_fname)

    def open(self, filename):
        """
        Open catalog file and read db
        Arguments:
            @filename - see MainModel __init__ docstring.
        Returns: Bool - true for success, false otherwise.
        """
        LOG.debug("filename: '%s'", filename)
        self.unsaved_project = False
        if not os.path.exists(filename):
            LOG.warn("db file '%s' doesn't exist.", filename)
            return False

        self.cat_fname = filename

        if self._open_or_decompress():
            return self._populate_discs_from_db()
        else:
            return False

    def new(self):
        """
        Create new catalog
        """
        self._cleanup_and_create_temp_db_file()

    def cleanup(self):
        """
        Remove temporary directory tree from filesystem
        """
        if self.tmp_filename is None:
            return

        try:
            os.unlink(self.tmp_filename)
            LOG.debug("file %s succesfully deleted", self.tmp_filename)
        except OSError:
            LOG.exception("temporary db file doesn't exists!")
        except TypeError:
            # TODO: file not exist - create? print error message?
            LOG.exception("temporary db file doesn't exists!")


    def _create_empty_db(self):
        """
        Create new DB
        """
        self._cleanup_and_create_temp_db_file()

    def _examine_file(self, filename):
        """
        Try to recognize file.
        Arguments:
            @filename - String with full path to file to examine
        Returns: 'sql', 'bz2' or None for file sqlite, compressed with bzip2
                  or other respectively
        """
        try:
            head_of_file = open(filename).read(15)
            LOG.debug("head of file: %s", filter(lambda x: x in printable,
                                                 head_of_file))
        except IOError:
            LOG.exception("Error opening file '%s'!", filename)
            self.cleanup()
            self.cat_fname = None
            self.tmp_filename = None
            return None

        if head_of_file == "SQLite format 3":
            LOG.debug("File format: uncompressed sqlite")
            return 'sql'
        elif head_of_file[0:10] == "BZh91AY&SY":
            LOG.debug("File format: bzip2")
            return 'bz2'
        else:
            return None

    def _open_or_decompress(self):
        """
        Try to open file, which user thinks is our catalog file.
        Returns: Bool - true for success, false otherwise
        """
        filename = os.path.abspath(self.cat_fname)
        LOG.info("catalog file: %s", filename)

        self._cleanup_and_create_temp_db_file()
        LOG.debug("tmp database file: %s", str(self.tmp_filename))

        examine = self._examine_file(filename)
        if examine == "sql":
            db_tmp = open(self.tmp_filename, "wb")
            db_tmp.write(open(filename).read())
            db_tmp.close()
        elif examine == "bz2":
            open_file = bz2.BZ2File(filename)
            try:
                db_tmp = open(self.tmp_filename, "w")
                db_tmp.write(open_file.read())
                db_tmp.close()
                open_file.close()
            except IOError:
                self.cleanup()
                self.filename = None
                self.internal_dirname = None
                LOG.exception("File is probably not a bz2!")
                return False
            if self._examine_file(self.tmp_filename) is not 'sql':
                LOG.error("Error opening file '%s' - not a catalog file!",
                          self.tmp_filename)
                self.cleanup()
                self.cat_fname = None
                self.tmp_filename = None
                return False

        else:
            LOG.error("Error opening file '%s' - not a catalog file!",
                      self.tmp_filename)
            self.cleanup()
            self.filename = None
            self.internal_dirname = None
            return False

        connect(os.path.abspath(self.tmp_filename))
        return True

    def _cleanup_and_create_temp_db_file(self):
        self.cleanup()
        fd, self.tmp_filename = mkstemp()
        # close file descriptor, otherwise it can be source of app crash!
        # http://www.logilab.org/blogentry/17873
        os.close(fd)

    def _populate_discs_from_db(self):
        """
        Read objects from database, fill TreeStore model with discs
        information
        """
        session = Session()
        dirs = session.query(File).filter(File.type == 1)
        dirs = dirs.order_by(File.filename).all()

        def get_children(parent_id=1, iterator=None):
            """
            Get all children of the selected parent.
            Arguments:
                @parent_id - integer with id of the parent (from db)
                @iterator - TODO
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
        session.close()

        return True

    def get_root_entries(self, id):
        LOG.debug("not implemented!, get_root_entries, id: %s", str(id))
