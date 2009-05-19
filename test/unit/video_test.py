"""
    Project: pyGTKtalog
    Description: Tests for Video class.
    Type: test
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2008-12-15
"""
import unittest
import os

from pygtktalog.video import Video


class TestVideo(unittest.TestCase):
    """Class for retrive midentify script output and put it in dict.
    Usually there is no need for such a detailed movie/clip information.
    Video script belongs to mplayer package.
    """

    def test_avi(self):
        """test mock avi file, should return dict with expected values"""
        avi = Video("mocks/m.avi")
        self.assertTrue(len(avi.tags) != 0, "result should have lenght > 0")
        self.assertEqual(avi.tags['audio_format'], '85')
        self.assertEqual(avi.tags['width'], 128)
        self.assertEqual(avi.tags['audio_no_channels'], 2)
        self.assertEqual(avi.tags['height'], 96)
        self.assertEqual(avi.tags['video_format'], 'XVID')
        self.assertEqual(avi.tags['length'], 4)
        self.assertEqual(avi.tags['audio_codec'], 'mp3')
        self.assertEqual(avi.tags['video_codec'], 'ffodivx')
        self.assertEqual(avi.tags['duration'], '00:00:04')
        self.assertEqual(avi.tags['container'], 'avi')

    def test_avi2(self):
        """test another mock avi file, should return dict with expected
        values"""
        avi = Video("mocks/m1.avi")
        self.assertTrue(len(avi.tags) != 0, "result should have lenght > 0")
        self.assertEqual(avi.tags['audio_format'], '85')
        self.assertEqual(avi.tags['width'], 128)
        self.assertEqual(avi.tags['audio_no_channels'], 2)
        self.assertEqual(avi.tags['height'], 96)
        self.assertEqual(avi.tags['video_format'], 'H264')
        self.assertEqual(avi.tags['length'], 4)
        self.assertEqual(avi.tags['audio_codec'], 'mp3')
        self.assertEqual(avi.tags['video_codec'], 'ffh264')
        self.assertEqual(avi.tags['duration'], '00:00:04')
        self.assertEqual(avi.tags['container'], 'avi')

    def test_mkv(self):
        """test mock mkv file, should return dict with expected values"""
        avi = Video("mocks/m.mkv")
        self.assertTrue(len(avi.tags) != 0, "result should have lenght > 0")
        self.assertEqual(avi.tags['audio_format'], '8192')
        self.assertEqual(avi.tags['width'], 128)
        self.assertEqual(avi.tags['audio_no_channels'], 2)
        self.assertEqual(avi.tags['height'], 96)
        self.assertEqual(avi.tags['video_format'], 'mp4v')
        self.assertEqual(avi.tags['length'], 4)
        self.assertEqual(avi.tags['audio_codec'], 'a52')
        self.assertEqual(avi.tags['video_codec'], 'ffodivx')
        self.assertEqual(avi.tags['duration'], '00:00:04')
        self.assertEqual(avi.tags['container'], 'mkv')

    def test_mpg(self):
        """test mock mpg file, should return dict with expected values"""
        avi = Video("mocks/m.mpg")
        self.assertTrue(len(avi.tags) != 0, "result should have lenght > 0")
        self.assertFalse(avi.tags.has_key('audio_format'))
        self.assertEqual(avi.tags['width'], 128)
        self.assertFalse(avi.tags.has_key('audio_no_channels'))
        self.assertEqual(avi.tags['height'], 96)
        self.assertEqual(avi.tags['video_format'], '0x10000001')
        self.assertFalse(avi.tags.has_key('lenght'))
        self.assertFalse(avi.tags.has_key('audio_codec'))
        self.assertEqual(avi.tags['video_codec'], 'ffmpeg1')
        self.assertFalse(avi.tags.has_key('duration'))
        self.assertEqual(avi.tags['container'], 'mpeges')

    def test_ogm(self):
        """test mock ogm file, should return dict with expected values"""
        avi = Video("mocks/m.ogm")
        self.assertTrue(len(avi.tags) != 0, "result should have lenght > 0")
        self.assertEqual(avi.tags['audio_format'], '8192')
        self.assertEqual(avi.tags['width'], 160)
        self.assertEqual(avi.tags['audio_no_channels'], 2)
        self.assertEqual(avi.tags['height'], 120)
        self.assertEqual(avi.tags['video_format'], 'H264')
        self.assertEqual(avi.tags['length'], 4)
        self.assertEqual(avi.tags['audio_codec'], 'a52')
        self.assertEqual(avi.tags['video_codec'], 'ffh264')
        self.assertEqual(avi.tags['duration'], '00:00:04')
        self.assertEqual(avi.tags['container'], 'ogg')

    def test_capture(self):
        """test capture with some small movie"""
        avi = Video("mocks/m.avi")
        filename = avi.capture()
        self.assertTrue(filename != None)
        self.assertTrue(os.path.exists(filename))
        file_size = os.stat(filename)[6]
        self.assertEqual(file_size, 9077)
        os.unlink(filename)


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
    unittest.main()
