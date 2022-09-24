"""
    Project: pyGTKtalog
    Description: Create thumbnail for sepcified image
    Type: lib
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2011-05-15
"""

import os
from tempfile import mkstemp
import shutil

from PIL import Image
import exifread

from pycatalog.logger import get_logger


LOG = get_logger(__name__)


class ThumbCreator(object):
    """
    Class for generate/extract thumbnail from image file
    """

    def __init__(self, filename):
        self.thumb_x = 160
        self.thumb_y = 160
        self.filename = filename

    def generate(self):
        """
        Save thumbnail into temporary file
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

        if exif and 'JPEGThumbnail' in exif and exif['JPEGThumbnail']:
            LOG.debug("exif thumb for filename %s" % self.filename)
            exif_thumbnail = exif['JPEGThumbnail']
            thumb = open(thumb_fn, 'wb')
            thumb.write(exif_thumbnail)
            thumb.close()
        else:
            LOG.debug("no exif thumb")
            if self.is_image_smaller():
                shutil.copyfile(self.filename, thumb_fn)
            else:
                thumb = self._scale_image()
                if thumb:
                    thumb.save(thumb_fn, "JPEG")

        if exif and 'Image Orientation' in exif:
            orient = exif['Image Orientation'].values[0]
            if orient > 1 and orient in orientations:
                thumb_image = Image.open(thumb_fn)
                tmp_thumb_img = thumb_image.transpose(orientations[orient])

                if orient in flips:
                    tmp_thumb_img = tmp_thumb_img.transpose(flips[orient])

                tmp_thumb_img.save(thumb_fn, 'JPEG')

        return thumb_fn

    def is_image_smaller(self):
        """Check if image is smaller than desired dimention, return boolean"""
        image = Image.open(self.filename)
        im_x, im_y = image.size
        image.close()
        return im_x <= self.thumb_x and im_y <= self.thumb_y

    def _get_exif(self):
        """
        Get exif (if available), return as a dict
        """
        image_file = open(self.filename, 'rb')
        try:
            exif = exifread.process_file(image_file)
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
        except Exception:
            return None
        it_x, it_y = image_thumb.size
        if it_x > self.thumb_x or it_y > self.thumb_y:
            image_thumb.thumbnail((self.thumb_x, self.thumb_y),
                                  Image.ANTIALIAS)
        return image_thumb
