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

from tempfile import gettempdir
from shutil import move
from os import path, mkdir
from datetime import datetime

from utils import EXIF
import Image

class Thumbnail(object):

    def __init__(self, filename=None, x=160, y=160,
                 root='thumbnails', base=''):
        self.root = root
        self.x = x
        self.y = y
        self.filename = filename
        self.base = base

    def save(self, image_id):
        """Save thumbnail into specific directory structure
        return full path to the file and exif object or None"""
        filepath = path.join(self.base, self.__get_and_make_path(image_id))
        f = open(self.filename, 'rb')
        exif = None
        returncode = -1
        try:
            exif = EXIF.process_file(f)
            f.close()
            if 'JPEGThumbnail' in exif:
                thumbnail = exif['JPEGThumbnail']
                f = open(filepath,'wb')
                f.write(thumbnail)
                f.close()
                if 'Image Orientation' in exif:
                    orientation = exif['Image Orientation'].values[0]
                    if orientation > 1:
                        # TODO: replace silly datetime function with tempfile
                        ms = datetime.now().microsecond
                        t = path.join(gettempdir(), "thumb%d.jpg" % ms)
                        im_in = Image.open(filepath)
                        im_out = None
                        if orientation == 8:
                            # Rotated 90 CCW
                            im_out = im_in.transpose(Image.ROTATE_90)
                        elif orientation == 6:
                            # Rotated 90 CW
                            im_out = im_in.transpose(Image.ROTATE_270)
                        elif orientation == 3:
                            # Rotated 180
                            im_out = im_in.transpose(Image.ROTATE_180)
                        elif orientation == 2:
                            # Mirrored horizontal
                            im_out = im_in.transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation == 4:
                            # Mirrored vertical
                            im_out = im_in.transpose(Image.FLIP_TOP_BOTTOM)
                        elif orientation == 5:
                            # Mirrored horizontal then rotated 90 CCW
                            op = Image.FLIP_LEFT_RIGHT
                            rot = Image.ROTATE_90
                            im_out = im_in.transpose(op).transpose(rot)
                        elif orientation == 7:
                            # Mirrored horizontal then rotated 90 CW
                            op = Image.FLIP_LEFT_RIGHT
                            rot = Image.ROTATE_270
                            im_out = im_in.transpose(op).transpose(rot)

                        if im_out:
                            im_out.save(t, 'JPEG')
                            move(t, filepath)
                        else:
                            f.close()
                returncode = 0
            else:
                im = self.__scale_image()
                if im:
                    im.save(filepath, "JPEG")
                    returncode = 1
        except:
            f.close()
            im = self.__scale_image()
            if im:
                im.save(filepath, "JPEG")
                returncode = 2
        return filepath, exif, returncode

    # private class functions
    def __get_and_make_path(self, img_id):
        """Make directory structure regards of id
        and return filepath WITHOUT extension"""
        t = path.join(self.base, self.root)
        try: mkdir(t)
        except: pass
        h = hex(img_id)
        if len(h[2:])>6:
            try: mkdir(path.join(t, h[2:4]))
            except: pass
            try: mkdir(path.join(t, h[2:4], h[4:6]))
            except: pass
            fpath = path.join(t, h[2:4], h[4:6], h[6:8])
            try: mkdir(fpath)
            except: pass
            img = "%s.%s" % (h[8:], 'jpg')
        elif len(h[2:])>4:
            try: mkdir(path.join(t, h[2:4]))
            except: pass
            fpath = path.join(t, h[2:4], h[4:6])
            try: mkdir(fpath)
            except: pass
            img = "%s.%s" % (h[6:], 'jpg')
        elif len(h[2:])>2:
            fpath = path.join(t, h[2:4])
            try: mkdir(fpath)
            except: pass
            img = "%s.%s" %(h[4:], 'jpg')
        else:
            fpath = ''
            img = "%s.%s" %(h[2:], 'jpg')
        return(path.join(t, fpath, img))

    def __scale_image(self, factor=True):
        """create thumbnail. returns image object or None"""
        try:
            im = Image.open(self.filename).convert('RGB')
        except:
            return None
        im.thumbnail((self.x, self.y), Image.ANTIALIAS)
        return im

    def __scale_image_deprecated(self, factor=True):
        """generate scaled Image object for given file
        args:
            factor - if False, adjust height into self.y
                     if True, use self.x for scale portrait pictures height.
            returns Image object, or None
        """
        try:
            im = Image.open(self.filename).convert('RGB')
        except:
            return None

        x, y = im.size

        if x > self.x or y > self.y:
            if x==y:
                # square
                imt = im.resize((self.y, self.y), Image.ANTIALIAS)
            elif x > y:
                # landscape
                if int(y/(x/float(self.x))) > self.y:
                    # landscape image: height is non standard
                    self.x1 = int(float(self.y) * self.y / self.x)
                    if float(self.y) * self.y / self.x - self.x1 > 0.49:
                        self.x1 += 1
                    imt = im.resize(((int(x/(y/float(self.y))), self.y)),
                                    Image.ANTIALIAS)
                elif x/self.x==y/self.y:
                    # aspect ratio ok
                    imt = im.resize((self.x, self.y), Image.ANTIALIAS)
                else:
                    imt = im.resize((self.x, int(y/(x/float(self.x)))), 1)
            else:
                # portrait
                if factor:
                    if y>self.x:
                        imt = im.resize(((int(x/(y/float(self.x))),self.x)),
                                        Image.ANTIALIAS)
                    else:
                        imt = im
                else:
                    self.x1 = int(float(self.y) * self.y / self.x)
                    if float(self.y) * self.y / self.x - self.x1 > 0.49:
                        self.x1 += 1

                    if x/self.x1==y/self.y:
                        # aspect ratio ok
                        imt = im.resize((self.x1,self.y),Image.ANTIALIAS)
                    else:
                        imt = im.resize(((int(x/(y/float(self.y))), self.y)),
                                        Image.ANTIALIAS)
            return imt
        else:
            return im

