"""
    Project: pyGTKtalog
    Description: Test simple dialogs
    Type: test
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-19
"""
import unittest
import os

import gtk

from pygtktalog.dialogs import Dialog, yesno, okcancel, info, warn, error


class MessageDialogMock(gtk.MessageDialog):
    """Mock class for MessageDialog, which shouldn't be displayed in a test"""

    def run(self):
        """Carefull! only for MESSAGE_INFO return value is RESPONSE_OK!"""
        if self.get_property('message-type') == gtk.MESSAGE_INFO:
            return gtk.RESPONSE_OK
        else:
            return gtk.RESPONSE_CANCEL

class TestDialog(unittest.TestCase):
    """Tests for Dialog class"""

    def test_dialog_create(self):
        """Test dialog creation and run method"""
        # overwrite MessageDialog class in gtk module
        gtk.MessageDialog = MessageDialogMock
        dialog = Dialog(gtk.MESSAGE_INFO, 'msg', 'secondarymsg', 'title')
        self.assertTrue(dialog.buttons == gtk.BUTTONS_OK, "dialog should have"
                        " gtk.BUTTONS_OK")
        self.assertTrue(dialog.run(), "dialog should return True")

        dialog = Dialog(gtk.MESSAGE_QUESTION, 'msg', 'secondarymsg', 'title')
        self.assertFalse(dialog.run(), "dialog should return False")
        # NOTE: dialog should be run before test against buttons attribute
        self.assertTrue(dialog.buttons == gtk.BUTTONS_YES_NO,
                        "dialog should have gtk.BUTTONS_YES_NO")

        dialog = Dialog(gtk.MESSAGE_QUESTION, 'msg', 'secondarymsg', 'title')
        dialog.buttons = gtk.BUTTONS_OK
        dialog.ok_default = True
        self.assertFalse(dialog.run(), "dialog should return True")

    def test_error(self):
        """Test error function"""
        result = error('msg', 'secondarymsg', 'title')
        self.assertTrue(result, "Should return True")

    def test_warn(self):
        """Test warn function"""
        result = warn('msg', 'secondarymsg', 'title')
        self.assertTrue(result, "Should return True")

    def test_info(self):
        """Test info function"""
        result = info('msg', 'secondarymsg', 'title')
        self.assertTrue(result, "Should return True")

    def test_yesno(self):
        """Test yesno function"""
        result = yesno('msg', 'secondarymsg', 'title')
        self.assertFalse(result, "Should return False")

    def test_okcancel(self):
        """Test yesno function"""
        result = okcancel('msg', 'secondarymsg', 'title')
        self.assertFalse(result, "Should return False")


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
    unittest.main()
