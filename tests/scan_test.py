"""
    Project: pyGTKtalog
    Description: Tests for scan files.
    Type: test
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2011-03-26
"""
import os
import shutil
import tempfile
import unittest

from pycatalog import scan
from pycatalog.dbobjects import File, Config, Image
from pycatalog.dbcommon import connect, Session


def populate_with_mock_files(dir_):
    """Make some files under specified directory, return number of files"""
    files1 = ['anim.mkv', 'text.txt', 'image.png', 'photoimage.jpg']
    files2 = ['music.mp3', 'loseless.flac']

    files_no = 0
    for file_ in files1:
        with open(os.path.join(dir_, file_), "wb") as fobj:
            fobj.write(b"\xde\xad\xbe\xef" * len(file_))
            files_no += 1

    os.symlink(os.path.join(dir_, files1[-1]), os.path.join(dir_, 'link.jpg'))
    files_no += 1

    os.mkdir(os.path.join(dir_, 'directory'))
    for file_ in files2:
        with open(os.path.join(dir_, 'directory', file_), "wb") as fobj:
            fobj.write(b"\xfe\xad\xfa\xce" * len(file_))
            files_no += 1

    return files_no


# TODO: exchange this with mock module
def _fake_video(obj, fobj, filepath):
    fobj.images.append(Image())
    fobj.images[0].filename = filepath + ".jpg"


def _fake_audio(obj, fobj, filepath):
    pass


def _fake_image(obj, fobj, filepath):
    pass


scan.Scan._video = _fake_video
scan.Scan._audio = _fake_audio
scan.Scan._image = _fake_image


class TestScan(unittest.TestCase):
    """
    Test cases for scan functionality

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
        self.image_path = tempfile.mkdtemp()
        self.scan_dir = tempfile.mkdtemp()
        self.no_of_files = populate_with_mock_files(self.scan_dir)

        connect()
        root = File()
        root.id = 1
        root.filename = 'root'
        root.size = 0
        root.source = 0
        root.type = 0
        root.parent_id = 1

        config = Config()
        config.key = 'image_path'
        config.value = self.image_path

        sess = Session()
        sess.add(root)
        sess.add(config)
        sess.commit()

    def tearDown(self):
        shutil.rmtree(self.image_path)
        shutil.rmtree(self.scan_dir)

    def test_happy_scenario(self):
        """
        make scan, count items
        """
        scanob = scan.Scan(self.scan_dir)
        result_list = scanob.add_files()

        # the number of added objects (files/links only) + "directory" +
        # topmost directory (self.scan_dir)
        self.assertEqual(len(result_list), self.no_of_files + 2)

        # all of topmost nide children - including "directory", but excluding
        # its contents - so it is all_files + 1 (directory) - 2 files from
        # subdir contents
        self.assertEqual(len(result_list[0].children), self.no_of_files - 1)
        # check soft links
        self.assertEqual(len([x for x in result_list if x.type == 3]), 1)

    def test_wrong_and_nonexistent(self):
        """
        Check for accessing non existent directory, regular file instead of
        the directory.
        """
        scanobj = scan.Scan('/nonexistent_directory_')
        self.assertRaises(OSError, scanobj.add_files)

        scanobj.path = '/root'
        self.assertRaises(scan.NoAccessError, scanobj.add_files)

        scanobj.path = '/bin/sh'
        self.assertRaises(scan.NoAccessError, scanobj.add_files)

    def test_abort_functionality(self):
        scanobj = scan.Scan(self.scan_dir)
        scanobj.abort = True
        self.assertEqual(None, scanobj.add_files())

    def test_double_scan(self):
        """
        Do the scan twice.
        """
        ses = Session()
        self.assertEqual(len(ses.query(File).all()), 1)

        scanob = scan.Scan(self.scan_dir)
        scanob.add_files()

        # dirs: main one + "directory" subdir
        self.assertEqual(len(ses.query(File).filter(File.type == 1).all()), 2)

        # files: '-1' for existing link there, which have it's own type
        self.assertEqual(len(ses.query(File).filter(File.type == 2).all()),
                         self.no_of_files - 1)
        # links
        self.assertEqual(len(ses.query(File).filter(File.type == 3).all()), 1)

        # all - sum of all of the above + root node
        self.assertEqual(len(ses.query(File).all()), self.no_of_files + 2 + 1)

        # it is perfectly ok, since we don't update collection, but just added
        # same directory twice.
        scanob2 = scan.Scan(self.scan_dir)
        scanob2.add_files()
        # we have twice as much of files (self.no_of_files), plus 2 * of
        # topmost dir and subdir "directory" (means 4) + root element
        self.assertEqual(len(ses.query(File).all()), self.no_of_files * 2 + 5)

        # get some movie files to examine
        file_ob = [x for x in scanob._files if x.filename == 'anim.mkv'][0]
        file2_ob = [x for x in scanob2._files if x.filename == 'anim.mkv'][0]

        # File objects are different
        self.assertTrue(file_ob is not file2_ob)

        # While Image objects points to the same file
        self.assertTrue(file_ob.images[0].filename ==
                        file2_ob.images[0].filename)

        # they are different objects
        self.assertTrue(file_ob.images[0] is not file2_ob.images[0])

        ses.close()


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
    unittest.main()
