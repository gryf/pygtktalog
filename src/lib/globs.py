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

import os.path
import sys

if sys.argv[0]:
    top_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    top_dir = "."

# ----------------------------------------------------------------------
TOPDIR = top_dir
RESOURCES_DIR = os.path.join(TOPDIR, "resources")
GLADE_DIR = os.path.join(RESOURCES_DIR, "glade")
STYLES_DIR = os.path.join(RESOURCES_DIR, "styles")
APPL_SHORT_NAME = "pygtktalog2"
APPL_VERSION = (1, 0, 2)
# ----------------------------------------------------------------------

