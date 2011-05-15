"""
    Project: pyGTKtalog
    Description: Tests for scan files.
    Type: test
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2011-03-26
"""
import os
import unittest

from pygtktalog import scan
from pygtktalog.dbobjects import File
from pygtktalog.dbcommon import connect, Session



class TestScan(unittest.TestCase):
    """
    Testcases for scan functionality

    1. execution scan function:
    1.1 simple case - should pass
    1.2 non-existent directory passed
    1.3 file passed
    1.4 directory has permission that forbids file listing

    2. rescan directory; looking for changes
    2.0 don't touch records for changed files (same directories, same
        filename, same type and size)
    2.1 search for files of the same type, same size.
    2.2 change parent node for moved files (don't insert new)

    3. adding new directory tree which contains same files like already stored
       in the database
    """
    def setUp(self):
        connect()
        root = File()
        root.id = 1
        root.filename = 'root'
        root.size = 0
        root.source = 0
        root.type = 0
        root.parent_id = 1

        sess = Session()
        sess.add(root)
        sess.commit()

    def test_happy_scenario(self):
        """
        make scan, count items
        """
        scanob = scan.Scan(os.path.abspath(os.path.join(__file__,
                                                        "../../../mocks")))
        scanob = scan.Scan("/mnt/data/_test_/test_dir")
        result_list = scanob.add_files()
        self.assertEqual(len(result_list), 143)
        self.assertEqual(len(result_list[0].children), 8)
        # check soft links
        self.assertEqual(len([x for x in result_list if x.type == 3]), 2)

    def test_wrong_and_nonexistent(self):
        """
        Check for accessing non existent directory, regular file instead of
        the directory, or file.directory with no access to it.
        """
        scanobj = scan.Scan('/nonexistent_directory_')
        self.assertRaises(OSError, scanobj.add_files)

        scanobj.path = '/root'
        self.assertRaises(scan.NoAccessError, scanobj.add_files)

        scanobj.path = '/bin/sh'
        self.assertRaises(scan.NoAccessError, scanobj.add_files)

        # dir contains some non accessable items. Should just pass, and on
        # logs should be messages about it
        scanobj.path = "/mnt/data/_test_/test_dir_permissions/"
        scanobj.add_files()

    def test_abort_functionality(self):
        scanobj = scan.Scan("/mnt/data/_test_/test_dir")
        scanobj.abort = True
        self.assertEqual(None, scanobj.add_files())

    def test_rescan(self):
        """
        Do the scan twice.
        """
        ses = Session()
        self.assertEqual(len(ses.query(File).all()), 1)

        scanob = scan.Scan("/mnt/data/_test_/test_dir")
        scanob.add_files()

        # note: we have 144 elements in db, because of root element
        self.assertEqual(len(ses.query(File).all()), 144)

        scanob2 = scan.Scan("/mnt/data/_test_/test_dir")
        scanob2.add_files()
        # it is perfectly ok, since we don't update collection, but just added
        # same directory twice.
        self.assertEqual(len(ses.query(File).all()), 287)
        file_ob = scanob._files[2]
        file2_ob = scanob2._files[2]

        # File objects are different
        self.assertTrue(file_ob.id != file2_ob.id)

        # While Image objects points to the same file
        self.assertTrue(file_ob.images[0].filename == \
                file2_ob.images[0].filename)

        # they are different objects
        self.assertTrue(file_ob.images[0].id != file2_ob.images[0].id)

        ses.close()

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
    unittest.main()
