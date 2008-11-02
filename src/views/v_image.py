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

import gtk

class ImageView(object):
    """simple image viewer. no scaling, no zooming, no rotating.
    simply show stupid image"""

    def __init__(self, image_filename):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        image = gtk.Image()
        image.set_from_file(image_filename)

        pixbuf = image.get_pixbuf()
        pic_width = pixbuf.get_width() + 23
        pic_height = pixbuf.get_height() + 23

        screen_width = gtk.gdk.screen_width()
        screen_height = gtk.gdk.screen_height()

        need_vieport = False
        if pic_height > (screen_height - 128):
            height = screen_height - 128
            need_vieport = True
        else:
            height = screen_height - 128

        if pic_width > (screen_width - 128):
            width = screen_width - 128
            need_vieport = True
        else:
            width = pic_width

        if need_vieport:
            window.resize(width, height)
            viewport = gtk.ScrolledWindow()
            viewport.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            viewport.add_with_viewport(image)
            window.add(viewport)
        else:
            window.add(image)
        window.show_all()
        return

    pass # end of class
