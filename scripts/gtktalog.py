#!/usr/bin/env python
"""
    Project: pyGTKtalog
    Description: Main gui file launcher
    Type: UI
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2016-08-19
"""
import sys
import tempfile
import os

from pygtktalog.dbobjects import File, Config
from pygtktalog.dbcommon import connect, Session
from pygtktalog.gtk2 import gui


class App(object):
    """Main app class"""

    def __init__(self, dbname):
        """Initialze"""
        self._dbname = None
        self.sess = Session()

        if dbname:
            self._dbname = dbname
            self.engine = connect(dbname)
        else:
            self._create_tmp_db()

        self.root = None
        self._dbname = dbname

    def _create_tmp_db(self):
        """Create temporatry db, untill user decide to save it"""
        fdsc, self._tmpdb = tempfile.mkstemp()
        os.close(fdsc)
        self.engine = connect(self._tmpdb)

        self.root = File()
        self.root.id = 1
        self.root.filename = 'root'
        self.root.size = 0
        self.root.source = 0
        self.root.type = 0
        self.root.parent_id = 1

        config = Config()
        config.key = "image_path"
        config.value = ":same_as_db:"

        self.sess.add(self.root)
        self.sess.add(config)
        self.sess.commit()

    def run(self):
        """Initialize gui"""
        gui.run()


def main():
    db = sys.argv if len(sys.argv) == 2 else None
    app = App(db)
    app.run()

if __name__ == "__main__":
    main()
