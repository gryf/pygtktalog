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
from shutil import move, copy
from os import path, mkdir
from datetime import datetime

from utils import EXIF
import Image

class Img(object):
    def __init__(self, filename=None, base=''):
        self.root = 'images'
        self.x = 96
        self.y = 96
        self.filename = filename
        self.base = base
        
    def save(self, image_id):
        """Save image and asociated thumbnail into specific directory structure
        return full path to the file and thumbnail None"""
        
        base_path = self.__get_and_make_path(image_id)
        ext = self.filename.split('.')[-1].lower()
        image_filename = path.join(self.base, base_path + "_im." + ext)
        
        # make and save image
        filepath = path.join(self.base, base_path + ".jpg")
        f = open(self.filename, 'rb')
        exif = None
        returncode = -1
        try:
            exif = EXIF.process_file(f)
            f.close()
            if exif.has_key('JPEGThumbnail'):
                thumbnail = exif['JPEGThumbnail']
                f = open(filepath,'wb')
                f.write(thumbnail)
                f.close()
                if exif.has_key('Image Orientation'):
                    orientation = exif['Image Orientation'].values[0]
                    if orientation > 1:
                        # TODO: replace silly datetime function with tempfile
                        t = path.join(gettempdir(), "thumb%d.jpg" % datetime.now().microsecond)
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
                            im_out = im_in.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
                        elif orientation == 7:
                            # Mirrored horizontal then rotated 90 CW
                            im_out = im_in.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
                            
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
                
        if returncode != -1:
            # copy image
            copy(self.filename, image_filename)
        return filepath, image_filename, returncode
        
    # private class functions
    def __get_and_make_path(self, img_id):
        """Make directory structure regards of id
        and return filepath and img filename WITHOUT extension"""
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
            img = "%s" % h[8:]
        elif len(h[2:])>4:
            try: mkdir(path.join(t, h[2:4]))
            except: pass
            fpath = path.join(t, h[2:4], h[4:6])
            try: mkdir(fpath)
            except: pass
            img = "%s" % h[6:]
        elif len(h[2:])>2:
            fpath = path.join(t, h[2:4])
            try: mkdir(fpath)
            except: pass
            img = "%s" % h[4:]
        else:
            fpath = ''
            img = "%s" % h[2:]
        return(path.join(t, fpath, img))
        
    def __scale_image(self, factor=True):
        """create thumbnail. returns image object or None"""
        try:
            im = Image.open(self.filename).convert('RGB')
        except:
            return None
        im.thumbnail((self.x, self.y), Image.ANTIALIAS)
        return im
