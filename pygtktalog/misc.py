"""
    Project: pyGTKtalog
    Description: Misc functions used more than once in src
    Type: lib
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-04-05
"""
import os
import errno
from zlib import crc32

import pygtktalog.dbcommon
from pygtktalog.logger import get_logger

LOG = get_logger(__name__)


def float_to_string(float_length):
    """
    Parse float digit into time string
    Arguments:
        @number - digit to be converted into time.
    Returns HH:MM:SS formatted string
    """
    hour = int(float_length / 3600)
    float_length -= hour*3600
    minutes = int(float_length / 60)
    float_length -= minutes * 60
    sec = int(float_length)
    return "%02d:%02d:%02d" % (hour, minutes, sec)

def calculate_image_path(dbpath=None, create=False):
    """Calculate image path out of provided path or using current connection"""
    if not dbpath:
        dbpath = pygtktalog.dbcommon.DbFilename
        if dbpath == ":memory:":
            raise OSError("Cannot create image path out of in-memory db!")

        dir_, file_ = (os.path.dirname(dbpath), os.path.basename(dbpath))
        file_base, dummy = os.path.splitext(file_)
        images_dir = os.path.join(dir_, file_base + "_images")
    else:
        if dbpath and "~" in dbpath:
            dbpath = os.path.expanduser(dbpath)
        if dbpath and "$" in dbpath:
            dbpath = os.path.expandvars(dbpath)
        images_dir = dbpath

    if create:
        if not os.path.exists(images_dir):
            try:
                os.mkdir(images_dir)
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise
    elif not os.path.exists(images_dir):
        raise OSError("%s: No such directory" % images_dir)

    return os.path.abspath(images_dir)

def mk_paths(fname, img_path):
    """Make path for provided pathname by calculating crc32 out of file"""
    with open(fname, 'r+b') as fobj:
        new_path = "%x" % (crc32(fobj.read(10*1024*1024)) & 0xffffffff)

    new_path = [new_path[i:i + 2] for i in range(0, len(new_path), 2)]
    full_path = os.path.join(img_path, *new_path[:-1])

    try:
        os.makedirs(full_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            LOG.debug("Directory %s already exists." % full_path)

    return new_path
