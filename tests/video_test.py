"""
    Project: pyGTKtalog
    Description: Tests for Video class.
    Type: test
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2008-12-15
"""
import os
import unittest
from unittest import mock
import io

import PIL

from pygtktalog.video import Video


DATA = {"m1.avi": """ID_VIDEO_ID=0
ID_AUDIO_ID=1
ID_FILENAME=m1.avi
ID_DEMUXER=avi
ID_VIDEO_FORMAT=H264
ID_VIDEO_BITRATE=46184
ID_VIDEO_WIDTH=128
ID_VIDEO_HEIGHT=96
ID_VIDEO_FPS=30.000
ID_VIDEO_ASPECT=0.0000
ID_AUDIO_FORMAT=85
ID_AUDIO_BITRATE=128000
ID_AUDIO_RATE=0
ID_AUDIO_NCH=0
ID_START_TIME=0.00
ID_LENGTH=4.03
ID_SEEKABLE=1
ID_CHAPTERS=0
ID_VIDEO_CODEC=ffh264
ID_AUDIO_BITRATE=128000
ID_AUDIO_RATE=22050
ID_AUDIO_NCH=2
ID_AUDIO_CODEC=mpg123
ID_EXIT=EOF
""",
        "m.avi": """ID_VIDEO_ID=0
ID_AUDIO_ID=1
ID_FILENAME=m.avi
ID_DEMUXER=avi
ID_VIDEO_FORMAT=XVID
ID_VIDEO_BITRATE=313536
ID_VIDEO_WIDTH=128
ID_VIDEO_HEIGHT=96
ID_VIDEO_FPS=30.000
ID_VIDEO_ASPECT=0.0000
ID_AUDIO_FORMAT=85
ID_AUDIO_BITRATE=128000
ID_AUDIO_RATE=0
ID_AUDIO_NCH=0
ID_START_TIME=0.00
ID_LENGTH=4.03
ID_SEEKABLE=1
ID_CHAPTERS=0
ID_VIDEO_CODEC=ffodivx
ID_AUDIO_BITRATE=128000
ID_AUDIO_RATE=22050
ID_AUDIO_NCH=2
ID_AUDIO_CODEC=mpg123
ID_EXIT=EOF""",
        "m.mkv": """ID_VIDEO_ID=0
ID_AUDIO_ID=0
ID_CLIP_INFO_NAME0=title
ID_CLIP_INFO_VALUE0=Avidemux
ID_CLIP_INFO_NAME1=encoder
ID_CLIP_INFO_VALUE1=Lavf51.12.1
ID_CLIP_INFO_N=2
ID_FILENAME=m.mkv
ID_DEMUXER=lavfpref
ID_VIDEO_FORMAT=MP4V
ID_VIDEO_BITRATE=0
ID_VIDEO_WIDTH=128
ID_VIDEO_HEIGHT=96
ID_VIDEO_FPS=30.000
ID_VIDEO_ASPECT=0.0000
ID_AUDIO_FORMAT=8192
ID_AUDIO_BITRATE=128000
ID_AUDIO_RATE=22050
ID_AUDIO_NCH=1
ID_START_TIME=0.00
ID_LENGTH=4.07
ID_SEEKABLE=1
ID_CHAPTERS=0
ID_VIDEO_CODEC=ffodivx
ID_AUDIO_BITRATE=128000
ID_AUDIO_RATE=22050
ID_AUDIO_NCH=1
ID_AUDIO_CODEC=ffac3
ID_EXIT=EOF""",
        "m.mpg": """ID_VIDEO_ID=0
ID_FILENAME=m.mpg
ID_DEMUXER=mpeges
ID_VIDEO_FORMAT=0x10000001
ID_VIDEO_BITRATE=2200000
ID_VIDEO_WIDTH=128
ID_VIDEO_HEIGHT=96
ID_VIDEO_FPS=30.000
ID_VIDEO_ASPECT=0.0000
ID_START_TIME=0.00
ID_LENGTH=0.97
ID_SEEKABLE=1
ID_CHAPTERS=0
ID_VIDEO_CODEC=ffmpeg1
ID_EXIT=EOF""",
        "m.ogm": """ID_VIDEO_ID=0
ID_AUDIO_ID=0
ID_FILENAME=m.ogm
ID_DEMUXER=lavfpref
ID_VIDEO_FORMAT=H264
ID_VIDEO_BITRATE=0
ID_VIDEO_WIDTH=160
ID_VIDEO_HEIGHT=120
ID_VIDEO_FPS=30.000
ID_VIDEO_ASPECT=0.0000
ID_AUDIO_FORMAT=8192
ID_AUDIO_BITRATE=128000
ID_AUDIO_RATE=22050
ID_AUDIO_NCH=1
ID_START_TIME=0.00
ID_LENGTH=4.00
ID_SEEKABLE=1
ID_CHAPTERS=0
ID_VIDEO_CODEC=ffh264
ID_AUDIO_BITRATE=128000
ID_AUDIO_RATE=22050
ID_AUDIO_NCH=1
ID_AUDIO_CODEC=ffac3
ID_EXIT=EOF""",
        "m.wmv": """ID_AUDIO_ID=1
ID_VIDEO_ID=2
ID_FILENAME=m.wmv
ID_DEMUXER=asf
ID_VIDEO_FORMAT=WMV3
ID_VIDEO_BITRATE=1177000
ID_VIDEO_WIDTH=852
ID_VIDEO_HEIGHT=480
ID_VIDEO_FPS=1000.000
ID_VIDEO_ASPECT=0.0000
ID_AUDIO_FORMAT=353
ID_AUDIO_BITRATE=0
ID_AUDIO_RATE=0
ID_AUDIO_NCH=0
ID_START_TIME=4.00
ID_LENGTH=4656.93
ID_SEEKABLE=1
ID_CHAPTERS=0
ID_VIDEO_CODEC=ffwmv3
ID_AUDIO_BITRATE=64028
ID_AUDIO_RATE=48000
ID_AUDIO_NCH=2
ID_AUDIO_CODEC=ffwmav2
ID_EXIT=EOF""",
        "m.mp4": """ID_VIDEO_ID=0
ID_AUDIO_ID=0
ID_AID_0_LANG=unk
ID_CLIP_INFO_NAME0=major_brand
ID_CLIP_INFO_VALUE0=isom
ID_CLIP_INFO_NAME1=minor_version
ID_CLIP_INFO_VALUE1=512
ID_CLIP_INFO_NAME2=compatible_brands
ID_CLIP_INFO_VALUE2=isomiso2avc1mp41
ID_CLIP_INFO_NAME3=encoder
ID_CLIP_INFO_VALUE3=Lavf56.25.101
ID_CLIP_INFO_N=4
ID_FILENAME=m.mp4
ID_DEMUXER=lavfpref
ID_VIDEO_FORMAT=H264
ID_VIDEO_BITRATE=1263573
ID_VIDEO_WIDTH=720
ID_VIDEO_HEIGHT=404
ID_VIDEO_FPS=25.000
ID_VIDEO_ASPECT=0.0000
ID_AUDIO_FORMAT=MP4A
ID_AUDIO_BITRATE=155088
ID_AUDIO_RATE=44100
ID_AUDIO_NCH=2
ID_START_TIME=0.00
ID_LENGTH=69.18
ID_SEEKABLE=1
ID_CHAPTERS=0
ID_VIDEO_CODEC=ffh264
ID_AUDIO_BITRATE=155082
ID_AUDIO_RATE=44100
ID_AUDIO_NCH=2
ID_AUDIO_CODEC=ffaac
ID_EXIT=EOF"""}


# TODO: exchange this with mock
class Readlines(object):
    def __init__(self, key=None):
        self.data = DATA.get(key, "")

    def readlines(self):
        return self.data.split('\n')


def mock_popen(command):
    key = None
    if 'midentify' in command:
        key = command.split('"')[1]
    elif 'jpeg:outdir' in command:
        # simulate capture for mplayer
        img_dir = command.split('"')[-2]
        img = PIL.Image.new('RGB', (320, 200))
        with open(os.path.join(img_dir, "00000001.jpg"), "wb") as fobj:
            img.save(fobj)

    return Readlines(key)


# os.popen = mock_popen


class TestVideo(unittest.TestCase):
    """test class for retrive midentify script output"""

    @mock.patch('os.popen')
    def test_avi(self, popen):
        """test mock avi file, should return dict with expected values"""
        fname = "m.avi"
        popen.return_value = io.StringIO(DATA[fname])
        avi = Video(fname)
        self.assertTrue(len(avi.tags) != 0, "result should have lenght > 0")
        self.assertEqual(avi.tags['audio_format'], '85')
        self.assertEqual(avi.tags['width'], 128)
        self.assertEqual(avi.tags['audio_no_channels'], 2)
        self.assertEqual(avi.tags['height'], 96)
        self.assertEqual(avi.tags['video_format'], 'xvid')
        self.assertEqual(avi.tags['length'], 4)
        self.assertEqual(avi.tags['audio_codec'], 'mpg123')
        self.assertEqual(avi.tags['video_codec'], 'ffodivx')
        self.assertEqual(avi.tags['duration'], '00:00:04')
        self.assertEqual(avi.tags['container'], 'avi')

    @mock.patch('os.popen')
    def test_avi2(self, popen):
        """test another mock avi file, should return dict with expected
        values"""
        fname = "m1.avi"
        popen.return_value = io.StringIO(DATA[fname])
        avi = Video(fname)
        self.assertTrue(len(avi.tags) != 0, "result should have lenght > 0")
        self.assertEqual(avi.tags['audio_format'], '85')
        self.assertEqual(avi.tags['width'], 128)
        self.assertEqual(avi.tags['audio_no_channels'], 2)
        self.assertEqual(avi.tags['height'], 96)
        self.assertEqual(avi.tags['video_format'], 'h264')
        self.assertEqual(avi.tags['length'], 4)
        self.assertEqual(avi.tags['audio_codec'], 'mpg123')
        self.assertEqual(avi.tags['video_codec'], 'ffh264')
        self.assertEqual(avi.tags['duration'], '00:00:04')
        self.assertEqual(avi.tags['container'], 'avi')

    @mock.patch('os.popen')
    def test_mkv(self, popen):
        """test mock mkv file, should return dict with expected values"""
        fname = "m.mkv"
        popen.return_value = io.StringIO(DATA[fname])
        mkv = Video(fname)
        self.assertTrue(len(mkv.tags) != 0, "result should have lenght > 0")
        self.assertEqual(mkv.tags['audio_format'], '8192')
        self.assertEqual(mkv.tags['width'], 128)
        self.assertTrue(mkv.tags['audio_no_channels'] in (1, 2))
        self.assertEqual(mkv.tags['height'], 96)
        self.assertEqual(mkv.tags['video_format'], 'mp4v')
        self.assertEqual(mkv.tags['length'], 4)
        self.assertTrue(mkv.tags['audio_codec'] in ('a52', 'ffac3'))
        self.assertEqual(mkv.tags['video_codec'], 'ffodivx')
        self.assertEqual(mkv.tags['duration'], '00:00:04')
        self.assertTrue(mkv.tags['container'] in ('mkv', 'lavfpref'))

    @mock.patch('os.popen')
    def test_mpg(self, popen):
        """test mock mpg file, should return dict with expected values"""
        fname = "m.mpg"
        popen.return_value = io.StringIO(DATA[fname])
        mpg = Video(fname)
        self.assertTrue(len(mpg.tags) != 0, "result should have lenght > 0")
        self.assertFalse('audio_format' in mpg.tags)
        self.assertEqual(mpg.tags['width'], 128)
        self.assertFalse('audio_no_channels' in mpg.tags)
        self.assertEqual(mpg.tags['height'], 96)
        self.assertEqual(mpg.tags['video_format'], '0x10000001')
        self.assertFalse('lenght' in mpg.tags)
        self.assertFalse('audio_codec' in mpg.tags)
        self.assertEqual(mpg.tags['video_codec'], 'ffmpeg1')
        self.assertFalse('duration' in mpg.tags)
        self.assertEqual(mpg.tags['container'], 'mpeges')

    @mock.patch('os.popen')
    def test_ogm(self, popen):
        """test mock ogm file, should return dict with expected values"""
        fname = "m.ogm"
        popen.return_value = io.StringIO(DATA[fname])
        ogm = Video(fname)
        self.assertTrue(len(ogm.tags) != 0, "result should have lenght > 0")
        self.assertEqual(ogm.tags['audio_format'], '8192')
        self.assertEqual(ogm.tags['width'], 160)
        self.assertTrue(ogm.tags['audio_no_channels'] in (1, 2))
        self.assertEqual(ogm.tags['height'], 120)
        self.assertEqual(ogm.tags['video_format'], 'h264')
        self.assertEqual(ogm.tags['length'], 4)
        self.assertTrue(ogm.tags['audio_codec'] in ('a52', 'ffac3'))
        self.assertEqual(ogm.tags['video_codec'], 'ffh264')
        self.assertEqual(ogm.tags['duration'], '00:00:04')
        self.assertTrue(ogm.tags['container'] in ('ogg', 'lavfpref'))

    @mock.patch('os.popen')
    def test_wmv(self, popen):
        """test mock wmv file, should return dict with expected values"""
        fname = "m.wmv"
        popen.return_value = io.StringIO(DATA[fname])
        wmv = Video(fname)
        self.assertTrue(len(wmv.tags) != 0, "result should have lenght > 0")
        self.assertEqual(wmv.tags['audio_format'], '353')
        self.assertEqual(wmv.tags['width'], 852)
        self.assertEqual(wmv.tags['audio_no_channels'], 2)
        self.assertEqual(wmv.tags['height'], 480)
        self.assertEqual(wmv.tags['video_format'], 'wmv3')
        self.assertEqual(wmv.tags['length'], 4656)
        self.assertEqual(wmv.tags['audio_codec'], 'ffwmav2')
        self.assertEqual(wmv.tags['video_codec'], 'ffwmv3')
        self.assertEqual(wmv.tags['duration'], '01:17:32')
        self.assertEqual(wmv.tags['container'], 'asf')

    @mock.patch('os.popen')
    def test_mp4(self, popen):
        """test mock mp4 file, should return dict with expected values"""
        fname = "m.mp4"
        popen.return_value = io.StringIO(DATA[fname])
        mp4 = Video(fname)
        self.assertTrue(len(mp4.tags) != 0, "result should have lenght > 0")
        self.assertEqual(mp4.tags['audio_format'], 'mp4a')
        self.assertEqual(mp4.tags['width'], 720)
        self.assertEqual(mp4.tags['audio_no_channels'], 2)
        self.assertEqual(mp4.tags['height'], 404)
        self.assertEqual(mp4.tags['video_format'], 'h264')
        self.assertEqual(mp4.tags['length'], 69)
        self.assertEqual(mp4.tags['audio_codec'], 'ffaac')
        self.assertEqual(mp4.tags['video_codec'], 'ffh264')
        self.assertEqual(mp4.tags['duration'], '00:01:09')
        self.assertEqual(mp4.tags['container'], 'lavfpref')

    @mock.patch('shutil.move')
    @mock.patch('pygtktalog.video.Image')
    @mock.patch('os.listdir')
    @mock.patch('shutil.rmtree')
    @mock.patch('os.close')
    @mock.patch('tempfile.mkstemp')
    @mock.patch('tempfile.mkdtemp')
    @mock.patch('os.popen')
    def test_capture(self, popen, mkdtemp, mkstemp, fclose, rmtree, listdir,
                     img, move):
        """test capture with some small movie and play a little with tags"""
        fname = 'm.avi'
        popen.return_value = io.StringIO(DATA[fname])
        mkdtemp.return_value = '/tmp'
        mkstemp.return_value = (10, 'foo.jpg')
        listdir.return_value = ['a.jpg', 'b.jpg', 'c.jpg', 'd.jpg']

        avi = Video(fname)
        filename = avi.capture()
        self.assertIsNotNone(filename)

        for length in (480, 380, 4):
            avi.tags['length'] = length
            filename = avi.capture()
            self.assertTrue(filename is not None)

        avi.tags['length'] = 3
        self.assertTrue(avi.capture() is None)

        avi.tags['length'] = 4

        avi.tags['width'] = 0
        self.assertTrue(avi.capture() is None)

        avi.tags['width'] = 1025
        filename = avi.capture()
        self.assertTrue(filename is not None)

        del(avi.tags['length'])
        self.assertTrue(avi.capture() is None)

        self.assertTrue(len(str(avi)) > 0)


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
    unittest.main()
