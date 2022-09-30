pycatalog
==========

Pycatalog is a commandline Linux/FreeBSD program for indexing CD, DVD, BR or
directories on filesystem. It is similar to `gtktalog`_ or `gwhere`_. There is
no coincidence in name of application, because it's meant to be replacement
(in some way) for gtktalog, which seems to be dead project for years.

Note, that even if it share same code base with pyGTKtalog, which was meant to
be desktop application, now pycatalog is pure console app, just for use with
commandline. You can find last version of pyGTKtalog under ``pyGTKtalog``
branch, although bear in mind, that it was written with `python 2.7`_ and
pyGTK_, which both are dead now.

Current version is 3.0.

Features
--------

* Scan for files in selected media
* Support for grouping files depending on file name (expected patterns in file
  names)
* Store selected EXIF tags
* Add/edit description and notes
* Fetch comments for images made in `gThumb`_
* `Tagging files`_
* And more :)

Requirements
------------

pycatalog requires python and following libraries:

* `python 3.10`_ and up
* `sqlalchemy 1.4`_
* `exifread`_ for parse EXIF information
* `mutagen`_ for extracting tags from audio files

Pycatalog extensively uses external programs in unix spirit, however there is
small possibility of using it Windows (probably with limitations) and quite big
possibility to run it on other sophisticated unix-like systems (i.e.
BeOS/ZETA/Haiku, QNX or MacOSX).

Programs that are used:
* ``midentify`` (provided by `mplayer`_ package)

For development process following programs are used:

* `nose`_
* `coverage`_
* `tox`_

Instalation
-----------

You don't have to install it if you don't want to. You can just change current
directory to pycatalog and simply run::

    $ paver run

That's it. Alternatively, if you like to put it in more system wide place, all
you have to do is:

#. put pycatalog directory into your destination of choice (/usr/local/share,
   /opt or ~/ is typical bet)

#. copy pycatalog shell script to /usr/bin, /usr/local/bin or in
   other place, where PATH variable is pointing or you feel like.

#. then modify pycatalog line 6 to match right ``pycatalog.py`` directory

Then, just run pycatalog script.

LICENSE
=======

This work is licensed under the terms of the GNU GPL, version 3. See the LICENCE
file in top-level directory.


.. _coverage: http://nedbatchelder.com/code/coverage/
.. _exifread: https://github.com/ianare/exif-py
.. _gthumb: http://gthumb.sourceforge.net
.. _gtktalog: http://www.nongnu.org/gtktalog/
.. _gwhere: http://www.gwhere.org/home.php3
.. _mplayer: http://mplayerhq.hu
.. _nose: http://code.google.com/p/python-nose/
.. _python 3.10: http://www.python.org/
.. _sqlalchemy 1.4: http://www.sqlalchemy.org
.. _tagging files: http://en.wikipedia.org/wiki/tag_%28metadata%29
.. _tox: https://testrun.org/tox
.. _mutagen: https://github.com/quodlibet/mutagen
