"""
    Project: pyGTKtalog
    Description: Thumbnail helper
    Type: library
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2012-02-19
"""
from hashlib import sha256
from cStringIO import StringIO

from lib import EXIF
import Image


class Thumbnail(object):
    """Class for generate/extract thumbnail from image file"""

    def __init__(self, fp, base=''):
        self.thumb_x = 160
        self.thumb_y = 160
        self.base = base
        self.sha256 = sha256(fp.read(10485760)).hexdigest()
        fp.seek(0)
        self.fp = fp

    def save(self):
        """Save thumbnail into specific directory structure
        return exif obj and fp to thumbnail"""
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

        try:
            exif = EXIF.process_file(self.fp)
        except:
            self.fp.seek(0)

        thumb_file = StringIO()
        if 'JPEGThumbnail' in exif:
            thumb_file.write(exif['JPEGThumbnail'])

            if 'Image Orientation' in exif:
                orient = exif['Image Orientation'].values[0]
                if orient > 1 and orient in orientations:
                    tmp_thumb_img = StringIO()

                    thumb_image = Image.open(self.fp)
                    tmp_thumb_img = thumb_image.transpose(orientations[orient])

                    if orient in flips:
                        tmp_thumb_img = tmp_thumb_img.transpose(flips[orient])

                    if tmp_thumb_img:
                        thumb_file.seek(0)
                        tmp_thumb_img.save(thumb_file, 'JPEG')
                    tmp_thumb_img.close()

        else:
            thumb = self.__scale_image()
            if thumb:
                thumb.save(self.thumbnail_path, "JPEG")

        return exif, thumb_file

    def __scale_image(self):
        """create thumbnail. returns image object or None"""
        try:
            image_thumb = Image.open(self.fp).convert('RGB')
        except:
            return None
        it_x, it_y = image_thumb.size
        if it_x > self.thumb_x or it_y > self.thumb_y:
            image_thumb.thumbnail((self.thumb_x, self.thumb_y),
                                  Image.ANTIALIAS)
        return image_thumb
