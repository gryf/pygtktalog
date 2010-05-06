"""
    Project: pyGTKtalog
    Description: Initialization for main module - i18n and so.
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-05
"""

__version__ = "1.9.0"

import os
import locale
import gettext
import __builtin__

import gtk.glade


__all__ = ['controllers',
           'models',
           'views',
           'EXIF',
           'dbcommon',
           'dbobjects',
           'dialogs',
           'logger',
           'misc']

GETTEXT_DOMAIN = 'pygtktalog'
# There should be message catalogs in "locale" directory placed by setup.py
# script. If there is no such directory, let's assume that message catalogs are
# placed in system wide location such as /usr/share/locale by Linux
# distribution package maintainer.
LOCALE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'locale')

try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    # unknown locale string, fallback to C
    locale.setlocale(locale.LC_ALL, 'C')

for module in gtk.glade, gettext:
    if os.path.exists(LOCALE_PATH):
        module.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
    else:
        module.bindtextdomain(GETTEXT_DOMAIN)
    module.textdomain(GETTEXT_DOMAIN)

# register the gettext function for the whole interpreter as "_"
__builtin__._ = gettext.gettext
