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
from xml.dom.minidom import Node
from xml.dom import minidom
import gzip
import os
from datetime import date

class GthumbCommentParser(object):
    def __init__(self, image_path, image_filename):
        self.path = image_path
        self.filename = image_filename
        
    def parse(self):
        """Return dictionary with apropriate fields, or None if no comment
        available"""
        try:
            gf = gzip.open(os.path.join(self.path,
                                        '.comments', self.filename + '.xml'))
        except:
            return None
            
        try:
            xml = gf.read()
            gf.close()
        except:
            gf.close()
            return None
            
        if not xml:
            return None

        retval = {}
        doc = minidom.parseString(xml)
        
        try:
            retval['note'] = doc.getElementsByTagName('Note').item(0).childNodes.item(0).data
        except: retval['note'] = None
            
        try:
            retval['place'] = doc.getElementsByTagName('Place').item(0).childNodes.item(0).data
        except: retval['place'] = None
        
        try:
            d = doc.getElementsByTagName('Time').item(0).childNodes.item(0).data
            if int(d) > 0: retval['date'] = date.fromtimestamp(int(d))
            else: retval['date'] = None
        except: retval['date'] = None
        
        try:
            retval['keywords'] = doc.getElementsByTagName('Keywords').item(0).childNodes.item(0).data.split(',')
        except: pass
        
        if len(retval) > 0: return retval
        else: return None
        
