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

from shutil import copy
from os import path, mkdir

import Image

class Img(object):

    def __init__(self, filename=None, base=''):
        self.root = 'images'
        self.x = 160
        self.y = 160
        self.filename = filename
        self.base = base

    def save(self, image_id):
        """Save image and asociated thumbnail into specific directory structure
        return full path to the file and thumbnail or None"""

        base_path = self.__get_and_make_path(image_id)
        ext = self.filename.split('.')[-1].lower()
        image_filename = path.join(self.base, base_path + "." + ext)

        thumbnail = path.join(self.base, base_path + "_t.jpg")

        returncode = -1

        im = self.__scale_image()
        if im:
            im.save(thumbnail, "JPEG")
            returncode = 1

        if returncode != -1:
            # copy image
            copy(self.filename, image_filename)

        return thumbnail, image_filename, returncode

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

    def __scale_image(self):
        """create thumbnail. returns image object or None"""
        try:
            im = Image.open(self.filename).convert('RGB')
        except:
            return None
        x, y = im.size
        if x > self.x or y > self.y:
            im.thumbnail((self.x, self.y), Image.ANTIALIAS)
        return im
