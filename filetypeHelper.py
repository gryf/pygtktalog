# This Python file uses the following encoding: utf-8
"""
functions for treat different files with different way
"""

import string
import os
import popen2

def guess_video(path):
    info = popen2.popen4('midentify "' + path + '"')[0].readlines()
    video_format = ''
    audio_codec = ''
    video_codec = ''
    video_x = ''
    video_y = ''
    for line in info:
        l = line.split('=')
        val = l[1].split('\n')[0]
        if l[0] == 'ID_VIDEO_FORMAT':
            video_format = val
        elif l[0] == 'ID_AUDIO_CODEC':
            audio_codec = val
        elif l[0] == 'ID_VIDEO_CODEC':
            video_codec = val
        elif l[0] == 'ID_VIDEO_WIDTH':
            video_x = val
        elif l[0] == 'ID_VIDEO_HEIGHT':
            video_y = val
    return (video_format,video_codec,audio_codec,video_x,video_y)
    
def guess_image(path):
    pass
