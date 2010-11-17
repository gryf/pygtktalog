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
        self.assertEqual(avi.tags['video_format'], 'xvid')
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
        self.assertEqual(avi.tags['video_format'], 'h264')
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
        self.assertTrue(avi.tags['audio_no_channels'] in (1, 2))
        self.assertEqual(avi.tags['height'], 96)
        self.assertEqual(avi.tags['video_format'], 'mp4v')
        self.assertEqual(avi.tags['length'], 4)
        self.assertTrue(avi.tags['audio_codec'] in ('a52', 'ffac3'))
        self.assertEqual(avi.tags['video_codec'], 'ffodivx')
        self.assertEqual(avi.tags['duration'], '00:00:04')
        self.assertTrue(avi.tags['container'] in ('mkv', 'lavfpref'))

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
        self.assertTrue(avi.tags['audio_no_channels'] in (1, 2))
        self.assertEqual(avi.tags['height'], 120)
        self.assertEqual(avi.tags['video_format'], 'h264')
        self.assertEqual(avi.tags['length'], 4)
        self.assertTrue(avi.tags['audio_codec'] in ('a52', 'ffac3'))
        self.assertEqual(avi.tags['video_codec'], 'ffh264')
        self.assertEqual(avi.tags['duration'], '00:00:04')
        self.assertTrue(avi.tags['container'] in ('ogg', 'lavfpref'))

    def test_capture(self):
        """test capture with some small movie and play a little with tags"""
        avi = Video("mocks/m.avi")
        filename = avi.capture()
        self.assertTrue(filename != None)
        self.assertTrue(os.path.exists(filename))
        file_size = os.stat(filename)[6]
        self.assertAlmostEqual(file_size/10000.0, 0.9, 0)
        os.unlink(filename)

        for length in (480, 380, 4):
            avi.tags['length'] = length
            filename = avi.capture()
            self.assertTrue(filename is not None)
            os.unlink(filename)

        avi.tags['length'] = 3
        self.assertTrue(avi.capture() is None)

        avi.tags['length'] = 4

        avi.tags['width'] = 0
        self.assertTrue(avi.capture() is None)

        avi.tags['width'] = 1025
        filename = avi.capture()
        self.assertTrue(filename is not None)
        os.unlink(filename)

        del(avi.tags['length'])
        self.assertTrue(avi.capture() is None)

        self.assertTrue(len(str(avi)) > 0)


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
    unittest.main()
