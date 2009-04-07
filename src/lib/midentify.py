"""
    Project: pyGTKtalog
    Description: Gather video file information. Uses external tools.
    Type: lib
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2008-12-15
"""
from os import popen
import sys

class Midentify(object):
    """Class for retrive midentify script output and put it in dict.
    Usually there is no need for such a detailed movie/clip information.
    Midentify script belongs to mplayer package.
    """

    def __init__(self, filename):
        """Init class instance. Filename of a video file is required."""
        self.filename = filename
        self.tags = {}

    def get_data(self):
        """return dict with clip information"""
        output = popen('midentify "%s"' % self.filename).readlines()

        attrs = {'ID_VIDEO_WIDTH': ['width', int],
                 'ID_VIDEO_HEIGHT': ['height', int],
                 'ID_LENGTH': ['length', lambda x: int(x.split(".")[0])],
                 # length is in seconds
                 'ID_DEMUXER': ['container', str],
                 'ID_VIDEO_FORMAT': ['video_format', str],
                 'ID_VIDEO_CODEC': ['video_codec', str],
                 'ID_AUDIO_CODEC': ['audio_codec', str],
                 'ID_AUDIO_FORMAT': ['audio_format', str],
                 'ID_AUDIO_NCH':  ['audio_no_channels', int],}

        for line in output:
            line = line.strip()
            for attr in attrs:
                if attr in line:
                    self.tags[attrs[attr][0]] = \
                        attrs[attr][1](line.replace("%s=" % attr, ""))

        if 'length' in self.tags:
            if self.tags['length'] > 0:
                hours = self.tags['length'] / 3600
                seconds = self.tags['length'] - hours * 3600
                minutes = seconds / 60
                seconds -= minutes * 60
                length_str = "%02d:%02d:%02d" % (hours, minutes, seconds)
                self.tags['duration'] = length_str
        return self.tags

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: %s filename" % sys.argv[0]
        sys.exit()

    for arg in sys.argv[1:]:
        mid = Midentify(arg)
        print mid.get_data()
