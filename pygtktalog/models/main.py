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
from sqlalchemy import create_engine

from pygtktalog.dbobjects import File, Exif, Group, Gthumb
from pygtktalog.dbobjects import Image, Tag, Thumbnail
from pygtktalog.dbcommon import connect, Meta, Session
from pygtktalog.logger import get_logger
from pygtktalog.models.details import DetailsModel
from pygtktalog.models.discs import DiscsModel
from pygtktalog.models.files import FilesModel

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
        self.config = {}
        # SQLAlchemy session object for internal use
        self._session = None
        # Flag indicates, that db was compressed
        # TODO: make it depend on configuration
        self.compressed = False

        self.db_unsaved = None

        self.discs = DiscsModel()
        self.files = FilesModel()

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
            return self.discs.refresh(self._session)
        else:
            return False

    def save(self, filename=None):
        """
        Save tared directory at given catalog fielname
        Arguments:
            @filename - see MainModel __init__ docstring.
        Returns: tuple:
            Bool - true for success, false otherwise.
            String or None - error message
        """

        if not filename and not self.cat_fname:
            LOG.debug("no filename detected!")
            return False, None

        if filename:
            if not '.sqlite' in filename:
                filename += '.sqlite'
            else:
                filename = filename[:filename.rindex('.sqlite')] + '.sqlite'

            if 'compress' in self.config and self.config['compress']:
                filename += '.bz2'

            self.cat_fname = filename
        val, err = self._compress_and_save()
        if not val:
            self.cat_fname = None
        return val, err

    def new(self):
        """
        Create new catalog
        """
        self.cleanup()
        self._create_temp_db_file()
        self._create_schema()
        self.discs.clear()
        self.files.clear()
        self.db_unsaved = False

    def cleanup(self):
        """
        Remove temporary directory tree from filesystem
        """

        if self._session:
            self._session.close()
            self._session = None

        if self.tmp_filename is None:
            return

        try:
            os.unlink(self.tmp_filename)
        except OSError:
            LOG.error("temporary db file doesn't exists!")
        except TypeError:
            # TODO: file does not exist - create? print error message?
            LOG.error("temporary db file doesn't exists!")
        else:
            LOG.debug("file %s succesfully deleted", self.tmp_filename)

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

        if self._session:
            self.cleanup()

        self._create_temp_db_file()
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
                self.cat_fname = None
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
            self.cat_fname = None
            self.internal_dirname = None
            return False

        connect(os.path.abspath(self.tmp_filename))
        self._session = Session()
        LOG.debug("session obj: %s" % str(self._session))
        return True

    def _create_temp_db_file(self):
        """
        Create new DB file, populate schema.
        """
        fd, self.tmp_filename = mkstemp()
        LOG.debug("new db filename: %s" % self.tmp_filename)
        # close file descriptor, otherwise it can be source of app crash!
        # http://www.logilab.org/blogentry/17873
        os.close(fd)

    def _create_schema(self):
        """
        """
        self._session = Session()
        LOG.debug("session obj: %s" % str(self._session))

        connect(os.path.abspath(self.tmp_filename))

        root = File()
        root.id = 1
        root.filename = 'root'
        root.size = 0
        root.source = 0
        root.type = 0
        root.parent_id = 1

        self._session.add(root)
        self._session.commit()

    def _compress_and_save(self):
        """
        Create (and optionaly compress) tar archive from working directory and
        write it to specified file.
        """

        # flush all changes
        self._session.commit()

        try:
            if 'compress' in self.config and self.config['compress']:
                output_file = bz2.BZ2File(self.cat_fname, "w")
            else:
                output_file = open(self.cat_fname, "w")
            LOG.debug("save (and optionally compress) successed")

        except IOError, (errno, strerror):
            LOG.error("error saving or compressing file", errno, strerror)
            return False, strerror

        dbpath = open(self.tmp_filename)
        output_file.write(dbpath.read())
        dbpath.close()
        output_file.close()

        self.db_unsaved = False
        return True, None
