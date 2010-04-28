"""
    Project: pyGTKtalog
    Description: Model for main application
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
import os
import bz2
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
    status_bar_message = _("Idle")
    current_disc = None

    __observables__ = ("status_bar_message", "current_disc")

    def __init__(self, filename=None):
        """Initialization. Make some nice defaults."""
        print "model"
        ModelMT.__init__(self)
        # Opened/saved database location in filesystem. Could be compressed.
        self.db_filename = filename
        # Temporary (usually in /tmp) working database.
        self.tmp_filename = None
        # Flag indicates, that db was compressed
        # TODO: make it depend on configuration
        self.compressed = False

        self.db_unsaved = False

        self.discs = gtk.TreeStore(str, gobject.TYPE_STRING)

        # XXX remove this on production!
        myiter = self.discs.insert_before(None, None)
        self.discs.set_value(myiter, 1, "bubu")
        self.discs.set_value(myiter, 1, "foo")
        self.discs.set_value(myiter, 1, "bar")

        itr = self.discs.append(None, None)
        self.discs.set_value(itr, 0, gtk.STOCK_DIRECTORY)
        self.discs.set_value(itr, 1, "foobar")
        for nr, name in enumerate(('foo', 'bar', 'baz')):
            self.discs.append(itr, (gtk.STOCK_FILE, "%s %d" % (name, nr)))

        #self.open()

    def open(self, filename=None):
        self.unsaved_project = False
        if filename is not None and not os.path.exists(filename):
            LOG.warn("db file '%s' doesn't exist", filename)
            return False

        if filename:
            self.db_filename = filename
        if self.db_filename:
            return self.__open_or_decompress()
        else:
            self.__create_empty_db()
        return True

    def cleanup(self):
        """remove temporary directory tree from filesystem"""
        if self.tmp_filename is None:
            return

        #import ipdb; ipdb.set_trace()
        LOG.debug("cleanup()")
        try:
            os.unlink(self.tmp_filename)
        except OSError:
            LOG.exception("temporary db file doesn't exists!")
        except TypeError:
            # TODO: file not exist - create? print error message?
            LOG.exception("temporary db file doesn't exists!")


    def __create_empty_db(self):
        pass

    def __open_or_decompress(self):
        filename = os.path.abspath(self.db_filename)
        LOG.info("database file: %s", filename)

        self.__cleanup_and_create_temp_db_file()
        LOG.debug("tmp database file: %s", str(self.tmp_filename))

        try:
            test_file = open(filename).read(15)
            LOG.debug("test_file: %s", test_file)
        except IOError:
            self.cleanup()
            self.db_filename = None
            self.tmp_filename = None
            LOG.exception("Error opening file!")
            return False

        if test_file == "SQLite format 3":
            db_tmp = open(self.tmp_filename, "wb")
            db_tmp.write(open(filename).read())
            db_tmp.close()
            LOG.debug("file format: sqlite")
        elif test_file[0:10] == "BZh91AY&SY":
            open_file = bz2.BZ2File(filename)
            try:
                db_tmp = open(self.tmp_filename, "w")
                db_tmp.write(open_file.read())
                db_tmp.close()
                open_file.close()
            except IOError:
                # file is not bz2
                self.cleanup()
                self.filename = None
                self.internal_dirname = None
                # TODO: add logger
                LOG.exception("File is probably not a bz2!")
                return False
        else:
            self.filename = None
            self.internal_dirname = None
            return False
        connect(os.path.abspath(self.tmp_filename))
        return True

    def __cleanup_and_create_temp_db_file(self):
        self.cleanup()
        fd, self.tmp_filename = mkstemp()
        # close file descriptor, otherwise it can be source of app crash!
        # http://www.logilab.org/blogentry/17873
        os.close(fd)

    # TODO: get this thing right
    def get_root_entries(self, id):
        LOG.debug("id: %s" (type(id)))
