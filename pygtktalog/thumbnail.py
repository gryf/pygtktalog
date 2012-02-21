"""
    Project: pyGTKtalog
    Description: Create thumbnail for sepcified image by its filename
    Type: lib
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2011-05-15
"""
import os
import sys
from cStringIO import StringIO
from tempfile import mkstemp

import Image

from pygtktalog.logger import get_logger
from pygtktalog import EXIF


LOG = get_logger(__name__)


class ThumbCreator(object):
    """
    Class for generate/extract thumbnail from image file
    """

    def __init__(self, filename):
        self.thumb_x = 160
        self.thumb_y = 160
        self.filename = filename.decode(sys.getfilesystemencoding())
        self.fobj = StringIO()

    def generate(self):
        """
        Generate and return file-like object with thumbnail
        """
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

        exif = self._get_exif()
        file_desc, thumb_fn = mkstemp(suffix=".jpg")
        os.close(file_desc)

        if 'JPEGThumbnail' not in exif:
            LOG.debug("no exif thumb for file %s; creating." % self.filename)
            thumb = self._scale_image()
            if thumb:
                thumb.save(self.fobj, "JPEG")
        else:
            LOG.debug("exif thumb for filename %s" % self.filename)
            exif_thumbnail = exif['JPEGThumbnail']
            self.fobj.write(exif_thumbnail)
            self.fobj.seek(0)

        if 'Image Orientation' in exif:
            orient = exif['Image Orientation'].values[0]
            if orient > 1 and orient in orientations:
                thumb_image = Image.open(self.fobj)
                tmp_thumb_img = thumb_image.transpose(orientations[orient])

                if orient in flips:
                    tmp_thumb_img = tmp_thumb_img.transpose(flips[orient])

                self.fobj.seek(0)
                self.fobj.truncate()
                tmp_thumb_img.save(self.fobj, 'JPEG')

        return self.fobj

    def _get_exif(self):
        """
        Get exif (if available), return as a dict
        """
        image_file = open(self.filename, 'rb')
        try:
            exif = EXIF.process_file(image_file)
        except Exception:
            exif = {}
            LOG.info("Exif crashed on '%s'." % self.filename)
        finally:
            image_file.close()

        return exif

    def _scale_image(self):
        """
        Create thumbnail. returns image object or None
        """
        try:
            image_thumb = Image.open(self.filename).convert('RGB')
        except:
            return None
        it_x, it_y = image_thumb.size
        if it_x > self.thumb_x or it_y > self.thumb_y:
            image_thumb.thumbnail((self.thumb_x, self.thumb_y),
                                  Image.ANTIALIAS)
        return image_thumb
