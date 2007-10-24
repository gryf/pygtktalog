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
"""
device (cd, dvd) helper
"""

import string
import os

def volname(mntp):
    """read volume name from cd/dvd"""
    dev = mountpoint_to_dev(mntp)
    if dev != None:
        try:
            a = open(dev,"rb")
            a.seek(32808)
            b = a.read(32).strip()
            a.close()
        except:
            return None
        return b
    return None
    
def volmount(mntp):
    """mount device, return True/False"""
    _in,_out,_err = os.popen3("mount %s" % mntp)
    inf = _err.readlines()
    if len(inf) > 0:
        for i in inf:
            i.strip()
        return i
    else:
        return 'ok'

def volumount(mntp):
    """mount device, return True/False"""
    _in,_out,_err = os.popen3("umount %s" % mntp)
    inf = _err.readlines()
    if len(inf) > 0:
        for error in inf:
            error.strip()
            
        if error.strip()[:7] == 'umount:':
            return error.strip()
    return 'ok'
    
def check_mount(dev):
    """Refresh the entries from fstab or mount."""
    mounts = os.popen('mount')
    for line in mounts.readlines():
        parts = line.split()
        device, txt1, mount_point, txt2, filesystem, options = parts
        if device == dev:
            return True
    return False

def mountpoint_to_dev(mntp):
    """guess mountpoint from fstab"""
    fstab = open("/etc/fstab")
    for line in fstab.readlines():
        a = line.split()
        try:
            if a[1] == mntp and a[0][0] != '#':
                fstab.close()
                return a[0]
        except:
            pass
    fstab.close()
    return None
    
def eject_cd(eject_app, cd):
    """mount device, return True/False"""
    if len(eject_app) > 0:
        _in,_out,_err = os.popen3("%s %s" % (eject_app, cd))
        inf = _err.readlines()
        error = ''
        
        for error in inf:
            error.strip()
            
        if error !='':
            return error
        
        return 'ok'
    return "Eject program not specified"
    
