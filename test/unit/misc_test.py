"""
    Project: pyGTKtalog
    Description: Tests for misc functions.
    Type: test
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-04-09
"""
import unittest
import os
import pygtktalog.misc as pgtkmisc

class TestMiscModule(unittest.TestCase):
    """
    Tests functions from misc module
    """

    def test_float_to_string(self):
        """
        test conversion between digits to formated output
        """
        self.assertEqual(pgtkmisc.float_to_string(10), '00:00:10')
        self.assertEqual(pgtkmisc.float_to_string(76), '00:01:16')
        self.assertEqual(pgtkmisc.float_to_string(22222), '06:10:22')
        self.assertRaises(TypeError, pgtkmisc.float_to_string)
        self.assertRaises(TypeError, pgtkmisc.float_to_string, None)
        self.assertRaises(TypeError, pgtkmisc.float_to_string, '10')

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
    print os.path.abspath(os.path.curdir)
    unittest.main()
