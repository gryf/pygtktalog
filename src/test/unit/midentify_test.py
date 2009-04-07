"""
    Project: pyGTKtalog
    Description: Tests for Midentify class.
    Type: test
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2008-12-15
"""
import unittest
from lib.midentify import Midentify

class TestMidentify(unittest.TestCase):
    """Class for retrive midentify script output and put it in dict.
    Usually there is no need for such a detailed movie/clip information.
    Midentify script belongs to mplayer package.
    """

    def test_avi(self):
        """test mock avi file, should return dict with expected values"""
        avi = Midentify("mocks/m.avi")
        result_dict = avi.get_data()
        self.assertTrue(len(result_dict) != 0, "result should have lenght > 0")
        self.assertEqual(result_dict['audio_format'], '85')
        self.assertEqual(result_dict['width'], 128)
        self.assertEqual(result_dict['audio_no_channels'], 2)
        self.assertEqual(result_dict['height'], 96)
        self.assertEqual(result_dict['video_format'], 'XVID')
        self.assertEqual(result_dict['length'], 4)
        self.assertEqual(result_dict['audio_codec'], 'mp3')
        self.assertEqual(result_dict['video_codec'], 'ffodivx')
        self.assertEqual(result_dict['duration'], '00:00:04')
        self.assertEqual(result_dict['container'], 'avi')

    def test_avi2(self):
        """test another mock avi file, should return dict with expected
        values"""
        avi = Midentify("mocks/m1.avi")
        result_dict = avi.get_data()
        self.assertTrue(len(result_dict) != 0, "result should have lenght > 0")
        self.assertEqual(result_dict['audio_format'], '85')
        self.assertEqual(result_dict['width'], 128)
        self.assertEqual(result_dict['audio_no_channels'], 2)
        self.assertEqual(result_dict['height'], 96)
        self.assertEqual(result_dict['video_format'], 'H264')
        self.assertEqual(result_dict['length'], 4)
        self.assertEqual(result_dict['audio_codec'], 'mp3')
        self.assertEqual(result_dict['video_codec'], 'ffh264')
        self.assertEqual(result_dict['duration'], '00:00:04')
        self.assertEqual(result_dict['container'], 'avi')

    def test_mkv(self):
        """test mock mkv file, should return dict with expected values"""
        avi = Midentify("mocks/m.mkv")
        result_dict = avi.get_data()
        self.assertTrue(len(result_dict) != 0, "result should have lenght > 0")
        self.assertEqual(result_dict['audio_format'], '8192')
        self.assertEqual(result_dict['width'], 128)
        self.assertEqual(result_dict['audio_no_channels'], 2)
        self.assertEqual(result_dict['height'], 96)
        self.assertEqual(result_dict['video_format'], 'mp4v')
        self.assertEqual(result_dict['length'], 4)
        self.assertEqual(result_dict['audio_codec'], 'a52')
        self.assertEqual(result_dict['video_codec'], 'ffodivx')
        self.assertEqual(result_dict['duration'], '00:00:04')
        self.assertEqual(result_dict['container'], 'mkv')

    def test_mpg(self):
        """test mock mpg file, should return dict with expected values"""
        avi = Midentify("mocks/m.mpg")
        result_dict = avi.get_data()
        self.assertTrue(len(result_dict) != 0, "result should have lenght > 0")
        self.assertFalse(result_dict.has_key('audio_format'))
        self.assertEqual(result_dict['width'], 128)
        self.assertFalse(result_dict.has_key('audio_no_channels'))
        self.assertEqual(result_dict['height'], 96)
        self.assertEqual(result_dict['video_format'], '0x10000001')
        self.assertFalse(result_dict.has_key('lenght'))
        self.assertFalse(result_dict.has_key('audio_codec'))
        self.assertEqual(result_dict['video_codec'], 'ffmpeg1')
        self.assertFalse(result_dict.has_key('duration'))
        self.assertEqual(result_dict['container'], 'mpeges')

    def test_ogm(self):
        """test mock ogm file, should return dict with expected values"""
        avi = Midentify("mocks/m.ogm")
        result_dict = avi.get_data()
        self.assertTrue(len(result_dict) != 0, "result should have lenght > 0")
        self.assertEqual(result_dict['audio_format'], '8192')
        self.assertEqual(result_dict['width'], 160)
        self.assertEqual(result_dict['audio_no_channels'], 2)
        self.assertEqual(result_dict['height'], 120)
        self.assertEqual(result_dict['video_format'], 'H264')
        self.assertEqual(result_dict['length'], 4)
        self.assertEqual(result_dict['audio_codec'], 'a52')
        self.assertEqual(result_dict['video_codec'], 'ffh264')
        self.assertEqual(result_dict['duration'], '00:00:04')
        self.assertEqual(result_dict['container'], 'ogg')

if __name__ == "__main__":
    unittest.main()
