# This Python file uses the following encoding: utf-8

from os import popen
from sys import argv, exit

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
        output = popen("midentify \"%s\"" % self.filename).readlines()
        for line in output:
            line = line.strip()
            if "ID_VIDEO_WIDTH" in line:
                self.tags['width'] = line.replace("ID_VIDEO_WIDTH=", "")
            elif "ID_VIDEO_HEIGHT" in line:
                self.tags['height'] = line.replace("ID_VIDEO_HEIGHT=", "")
            elif "ID_LENGTH" in line:
                length = line.replace("ID_LENGTH=", "")
                if "." in length:
                    length = length.split(".")[0]
                seconds = int(length)
                if seconds > 0:
                    hours = seconds / 3600
                    seconds -= hours * 3600
                    minutes = seconds / 60
                    seconds -= minutes * 60
                    self.tags['length'] = length
                    length_str = "%02d:%02d:%02d" % (hours, minutes, seconds)
                    self.tags['duration'] = length_str
            elif "ID_DEMUXER" in line:
                self.tags['container'] = line.replace("ID_DEMUXER=", "")
            elif "ID_VIDEO_FORMAT" in line:
                self.tags['video_format'] = line.replace("ID_VIDEO_FORMAT=", "")
            elif "ID_VIDEO_CODEC" in line:
                self.tags['video_codec'] = line.replace("ID_VIDEO_CODEC=", "")
            elif "ID_AUDIO_CODEC" in line:
                self.tags['audio_codec'] = line.replace("ID_AUDIO_CODEC=", "")
            elif "ID_AUDIO_FORMAT" in line:
                self.tags['audio_format'] = line.replace("ID_AUDIO_FORMAT=", "")
            elif "ID_AUDIO_NCH" in line:
                self.tags['audio_no_channels'] = line.replace("ID_AUDIO_NCH=",
                                                              "")
        return self.tags


if __name__ == "__main__":
    """run as standalone script"""
    if len(argv) < 2:
        print "usage: %s filename" % argv[0]
        exit()
        
    for arg in argv[1:]:
        mid = Midentify(arg)
        print mid.get_data()
