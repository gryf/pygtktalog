"""
    Project: pyGTKtalog
    Description: Test harvester and runner.
    Type: exec
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2008-12-15
"""
import sys
import unittest
from os import path, chdir
import glob


def setup_path():
    """Sets up the python include paths to include needed directories"""
    this_path = path.abspath(path.dirname(__file__))
    sys.path = [path.join(this_path, "../../src")] + sys.path
    sys.path = [path.join(this_path, "../../src/test/unit")] + sys.path
    return

def build_suite():
    """Build suite test from files in unit directory. Filenames with test
    suites should always end with "_test.py"."""
    modules = []
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

    modules = map(__import__, modules)
    load = unittest.defaultTestLoader.loadTestsFromModule
    return unittest.TestSuite(map(load, modules))

if __name__ == "__main__":
    chdir(path.abspath(path.curdir))
    setup_path()
    unittest.main(defaultTest="build_suite")

