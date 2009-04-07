"""
    Project: pyGTKtalog
    Description: Simple functions for device management.
    Type: lib
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2008-12-15
"""
import os
import locale
import gettext

from src.lib.globs import APPL_SHORT_NAME

locale.setlocale(locale.LC_ALL, '')
gettext.install(APPL_SHORT_NAME, 'locale', unicode=True)

def volname(mntp):
    """read volume name from cd/dvd"""
    dev = mountpoint_to_dev(mntp)
    label = None
    if dev != None:
        try:
            disk = open(dev, "rb")
            disk.seek(32808)
            label = disk.read(32).strip()
            disk.close()
        except IOError:
            return None
    return label

def volmount(mntp):
    """
    Mount device.
    @param mountpoint
    @returns tuple with bool status of mount, and string with error message
    """
    _in, _out, _err = os.popen3("mount %s" % mntp)
    inf = _err.readlines()
    if len(inf) > 0:
        return False, inf[0].strip()
    else:
        return True, ''

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
    return _("Eject program not specified")

