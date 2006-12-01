# This Python file uses the following encoding: utf-8
"""
device (cd, dvd) helper
"""

import string
import os
import popen2

from config import Config

c = Config()

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
    dev = mountpoint_to_dev(mntp)
    if dev != None:
        _in,_out,_err = popen2.popen3("mount %s" % dev)
        inf = _err.readlines()
        for i in inf:
            i.strip()
        if check_mount(dev):
            return 'ok'
        else:
            return i.strip()
    return "Mount point does'nt exist in fstab"

def volumount(mntp):
    """mount device, return True/False"""
    dev = mountpoint_to_dev(mntp)
    if dev != None:
        _in,_out,_err = popen2.popen3("umount %s" % dev)
        inf = _err.readlines()
        for i in inf:
            i.strip()
        if check_mount(dev):
            return 'ok'
        else:
            return i.strip()
    return "Mount point does'nt exist in fstab"
    
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
    
def eject_cd():
    if len(c.confd['ejectapp']) > 0:
        os.popen("%s %s" %(c.confd['ejectapp'],c.confd['cd']))

