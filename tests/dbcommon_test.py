"""
    Project: pyGTKtalog
    Description: Tests for DataBase class.
    Type: test
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-07-19
"""
import unittest
import os

from pycatalog.dbcommon import connect


class TestDataBase(unittest.TestCase):
    """
    Class responsible for database connection and schema creation
    """

    def test_connect(self):
        """
        Test connection to database. Memory and file method will be tested.
        """
        connect(":memory:")


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
    unittest.main()
