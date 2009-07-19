"""
    Project: pyGTKtalog
    Description: Tests for DataBase class.
    Type: test
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-07-19
"""
import unittest
import os
from tempfile import mkstemp

from pygtktalog.dbcommon import DataBase, create_database


class TestDataBase(unittest.TestCase):
    """
    Class responsible for database connection and schema creation
    """

    def tearDown(self):
        """
        Tear down method. Close db connection.
        """
        DataBase.close()

    def test_connect(self):
        """
        Test connection to database. Memory and file method will be tested.
        """
        DataBase.filename = ":memory:"
        cursor = DataBase.connect()
        self.assertTrue(cursor)
        self.assertTrue(cursor == DataBase.connect())
        DataBase.close()

        file_desc, dbfilename = mkstemp()
        os.close(file_desc)

        DataBase.filename = dbfilename
        cursor = DataBase.connect()

        self.assertTrue(cursor)
        self.assertTrue(cursor == DataBase.connect())
        DataBase.close()

        os.unlink(dbfilename)

    def test_close(self):
        """
        Test close method
        """
        DataBase.filename = ":memory:"
        DataBase.connect()

        self.assertFalse(DataBase.cur is None)
        self.assertFalse(DataBase.conn is None)
        self.assertFalse(DataBase.filename is None)

        result = DataBase.close()

        self.assertTrue(result, "Should ne True, but was %s" % str(result))
        self.assertTrue(DataBase.cur is None)
        self.assertTrue(DataBase.conn is None)
        self.assertTrue(DataBase.filename is None)

        self.assertFalse(DataBase.close())

    def test_get_cursor(self):
        """
        Test get_cursor() method.
        """
        cur = DataBase.get_cursor()
        self.assertEqual(cur, None, "Cursor should be None")

        DataBase.filename = ":memory:"
        DataBase.connect()

        cur = DataBase.get_cursor()
        self.assertNotEqual(cur, None, "Cursor shouldn't be None")

    def test_get_cconnection(self):
        """
        Test get_connection() method.
        """
        conn = DataBase.get_connection()
        self.assertEqual(conn, None, "Connection object should be None")

        DataBase.filename = ":memory:"
        DataBase.connect()

        conn = DataBase.get_connection()
        self.assertNotEqual(conn, None, "Connection object shouldn't be None")

    def test_check_schema(self):
        """
        Test check_schema() method.
        """

        self.assertFalse(DataBase.check_schema())

        DataBase.filename = ":memory:"
        DataBase.connect()

        self.assertFalse(DataBase.check_schema())

        DataBase.create_schema(DataBase.cur, DataBase.conn)

        self.assertTrue(DataBase.check_schema())

    def test_create_schema(self):
        """
        Test create_schema() method.
        """
        self.assertFalse(DataBase.create_schema(DataBase.cur, DataBase.conn))

        DataBase.filename = ":memory:"
        DataBase.connect()

        result = DataBase.create_schema(DataBase.cur, DataBase.conn)
        self.assertTrue(result, "%s" % result)

        self.assertTrue(DataBase.check_schema())

    def test_create_database(self):
        """
        Test create_database function
        """
        create_database()
        self.assertTrue(True)


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
    unittest.main()
