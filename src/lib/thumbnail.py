# This Python file uses the following encoding: utf-8
#
#  Author: Roman 'gryf' Dobosz  gryf@elysium.pl
#
#  Copyright (C) 2007 by Roman 'gryf' Dobosz
#
#  This file is part of pyGTKtalog.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

#  -------------------------------------------------------------------------

from tempfile import mkstemp
from hashlib import sha512
from shutil import move
from os import path
import sys

from lib import EXIF
import Image

class Thumbnail(object):
    """Class for generate/extract thumbnail from image file"""

    def __init__(self, filename=None, base=''):
        self.thumb_x = 160
        self.thumb_y = 160
        self.filename = filename
        self.base = base
        self.sha512 = sha512(open(filename).read()).hexdigest()
        self.thumbnail_path = path.join(self.base, self.sha512 + "_t")

    def save(self):
        """Save thumbnail into specific directory structure
        return filename base and exif object or None"""
        exif = {}
        orientations = {2: Image.FLIP_LEFT_RIGHT,  # Mirrored horizontal
                        3: Image.ROTATE_180,       # Rotated 180
                        4: Image.FLIP_TOP_BOTTOM,  # Mirrored vertical
                        5: Image.ROTATE_90,        # Mirrored horizontal then
                                                   # rotated 90 CCW
                        6: Image.ROTATE_270,       # Rotated 90 CW
                        7: Image.ROTATE_270,       # Mirrored horizontal then
                                                   # rotated 90 CW
                        8: Image.ROTATE_90}        # Rotated 90 CCW
        flips = {7: Image.FLIP_LEFT_RIGHT, 5: Image.FLIP_LEFT_RIGHT}

        image_file = open(self.filename, 'rb')
        try:
            exif = EXIF.process_file(image_file)
        except:
            if __debug__:
                print "exception", sys.exc_info()[0], "raised with file:"
                print self.filename
        finally:
            image_file.close()

        if path.exists(self.thumbnail_path):
            if __debug__:
                print "file", self.filename, "with hash", self.sha512, "exists"
            return self.sha512, exif

        if 'JPEGThumbnail' in exif:
            if __debug__:
                print self.filename, "exif thumb"
            exif_thumbnail = exif['JPEGThumbnail']
            thumb_file = open(self.thumbnail_path, 'wb')
            thumb_file.write(exif_thumbnail)
            thumb_file.close()

            if 'Image Orientation' in exif:
                orient = exif['Image Orientation'].values[0]
                if orient > 1 and orient in orientations:
                    fd, temp_image_path = mkstemp()
                    os.close(fd)

                    thumb_image = Image.open(self.thumbnail_path)
                    tmp_thumb_img = thumb_image.transpose(orientations[orient])

                    if orient in flips:
                        tmp_thumb_img = tmp_thumb_img.transpose(flips[orient])

                    if tmp_thumb_img:
                        tmp_thumb_img.save(temp_image_path, 'JPEG')
                        move(temp_image_path, self.thumbnail_path)
            return self.sha512, exif
        else:
            if __debug__:
                print self.filename, "no exif thumb"
            thumb = self.__scale_image()
            if thumb:
                thumb.save(self.thumbnail_path, "JPEG")
                return self.sha512, exif
        return None, exif

    def __scale_image(self):
        """create thumbnail. returns image object or None"""
        try:
            image_thumb = Image.open(self.filename).convert('RGB')
        except:
            return None
        it_x, it_y = image_thumb.size
        if it_x > self.thumb_x or it_y > self.thumb_y:
            image_thumb.thumbnail((self.thumb_x, self.thumb_y), Image.ANTIALIAS)
        return image_thumb
