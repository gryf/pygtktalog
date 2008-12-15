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

import os

def volname(mntp):
    """read volume name from cd/dvd"""
    dev = mountpoint_to_dev(mntp)
    if dev != None:
        try:
            disk = open(dev, "rb")
            disk.seek(32808)
            label = disk.read(32).strip()
            disk.close()
        except IOError:
            return None
        return label
    return None

def volmount(mntp):
    """mount device, return 'ok' or error message"""
    _in, _out, _err = os.popen3("mount %s" % mntp)
    inf = _err.readlines()
    if len(inf) > 0:
        return inf[0].strip()
    else:
        return 'ok'

def volumount(mntp):
    """mount device, return 'ok' or error message"""
    _in, _out, _err = os.popen3("umount %s" % mntp)
    inf = _err.readlines()
    if len(inf) > 0:
        return inf[0].strip()
    return 'ok'

def check_mount(dev):
    """Refresh the entries from fstab or mount."""
    mounts = os.popen('mount')
    for line in mounts.readlines():
        parts = line.split()
        device = parts
        if device[0] == dev:
            return True
    return False

def mountpoint_to_dev(mntp):
    """guess device name by mountpoint from fstab"""
    fstab = open("/etc/fstab")
    device = None
    for line in fstab.readlines():
        output = line.split()
        # lengtht of single valid  fstab line is at least 5
        if len(output) > 5 and output[1] == mntp and output[0][0] != '#':
            device = output[0]

    fstab.close()
    return device

def eject_cd(eject_app, cdrom):
    """mount device, return 'ok' or error message"""
    if len(eject_app) > 0:
        _in, _out, _err = os.popen3("%s %s" % (eject_app, cdrom))
        inf = _err.readlines()

        if len(inf) > 0 and inf[0].strip() != '':
            return inf[0].strip()

        return 'ok'
    return "Eject program not specified"

