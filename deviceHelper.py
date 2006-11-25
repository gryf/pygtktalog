#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
device (cd, dvd) helper
"""

import string
import os

def volname(dev):
    """read volume name from cd/dvd"""
    try:
        a = open(dev,"rb")
        a.seek(32808)
        b = a.read(32).strip()
        a.close()
    except:
        return None
    return b
    
def volmount(dev):
    """mount device, return True/False"""
    stout,stin,sterr = popen3("mount %s" % dev)
    error = sterr.readline()
    stout.close()
    stin.close()
    sterr.close()
    return len(error) == 0
