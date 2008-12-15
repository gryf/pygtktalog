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
from os import path
from hashlib import sha512

import Image

class Img(object):

    def __init__(self, filename, base=''):
        self.root = 'images'
        self.x = 160
        self.y = 160
        self.filename = filename
        self.base = base
        f = open(filename, "r")
        self.sha512 = sha512(f.read()).hexdigest()
        f.close()

    def save(self):
        """Save image and asociated thumbnail into specific directory structure
        returns filename for image"""

        
        image_filename = path.join(self.base, self.sha512)
        thumbnail = path.join(self.base, self.sha512 + "_t")
        
        # check wheter image already exists
        if path.exists(image_filename) and path.exists(thumbnail):
            if __debug__:
                print "image", self.filename, "with hash",
                print self.sha512, "already exist"
            return self.sha512

        if not path.exists(thumbnail):
            im = self.__scale_image()
            im.save(thumbnail, "JPEG")

        # copy image
        if not path.exists(image_filename):
            copy(self.filename, image_filename)

        return self.sha512

    # private class functions
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
