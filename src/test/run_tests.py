#!/usr/bin/env python
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
import sys
import unittest
from os import path, chdir
import glob


def my_import(module, name):
    """import replacement"""
    mod = __import__(module, {}, {}, [name])
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def setup_path():
    """Sets up the python include paths to include needed directories"""
    this_path = path.abspath(path.dirname(__file__))
    sys.path = [path.join(this_path, "../../src")] + sys.path
    sys.path = [path.join(this_path, "../../src/test")] + sys.path
    sys.path = [path.join(this_path, "../../src/test/unit")] + sys.path
    return

def build_suite():
    """build suite test from files in unit directory"""
    modules = []
    classes = []
    for fname in glob.glob1('unit', '*_test.py'):
        class_name = fname[:-8]
        if "_" in class_name:
            splited = class_name.split("_")
            class_name = 'Test'
            for word in splited:
                class_name += word.capitalize()
        else:
            class_name = "Test" + class_name.capitalize()

        modules.append(fname[:-3])
        classes.append(class_name)

    modules = map(__import__, modules)
    load = unittest.defaultTestLoader.loadTestsFromModule
    return unittest.TestSuite(map(load, modules))

if __name__ == "__main__":
    chdir(path.abspath(path.curdir))
    setup_path()
    unittest.main(defaultTest="build_suite")

