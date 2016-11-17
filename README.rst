pyGTKtalog
==========

Pygtktalog is Linux/FreeBSD program for indexing CD, DVD, BR or directories on
filesystem. It is similar to `gtktalog`_ or `gwhere`_. There is no coincidence
in name of application, because it's meant to be replacement (in some way) for
gtktalog, which seems to be dead project for years.

Current version is 2.0.

FEATURES
--------

* Scan for files in selected media
* Support for grouping files depending on file name (expected patterns in file
  names)
* Get/generate thumbnails from EXIF and other images
* Store selected EXIF tags
* Add/edit description and notes
* Fetch comments for images made in `gThumb`_
* Add/remove unlimited images to any file or directory
* `Tagging files`_
* And more :)

Frontends
---------

New version of pyGTKtalog was meant to use multiple interfaces.

#. First for the new incarnation of pyGTKtalog is… command line tool for
   accessing catalog dbs. With ``cmdcatalog.py`` it's possible to:

   * create new catalog
   * update it
   * list
   * find files
   * fsck (for maintenance for orphaned thumbs/images)

#. ``gtktalog.py``. This is written from scratch frontend in pygtk. Still work
   in progress.

Requirements
------------

pyGTKtalog requires python and following libraries:

* `python 2.7`_
* `sqlalchemy 1.0`_
* `pygtk 2.24`_ (only for ``gtktalog.py``)

It may work on other (lower) version of libraries, and it should work with
higher versions of libraries, although it will not work on Python 3 yet, nor
GTK3.

Optional modules
^^^^^^^^^^^^^^^^

* `PIL`_ for image manipulation

Additional pyGTKtalog uses `EXIF`_ module by Gene Cash (slightly updated to EXIF
2.2 by me) which is included in sources.

pyGTKtalog extensively uses external programs in unix spirit, however there is
small possibility of using it Windows (probably with limitations) and quite big
possibility to run it on other sophisticated unix-like systems (i.e.
BeOS/ZETA/Haiku, QNX or MacOSX).

Programs that are used:
* ``mencoder`` (provided by `mplayer`_ package)
* ``montage``, ``convert`` from `ImageMagick`_

For development process following programs are used:

* `gettext`_
* `intltool`_
* `nose`_
* `coverage`_
* `paver`_
* `tox`_

INSTALATION
-----------

You don't have to install it if you don't want to. You can just change current
directory to pyGTKtalog and simply run::

    $ paver run

That's it. Alternatively, if you like to put it in more system wide place, all
you have to do is:

#. put pyGTKtalog directory into your destination of choice (/usr/local/share,
   /opt or ~/ is typical bet)

#. copy pyGTKtalog shell script to /usr/bin, /usr/local/bin or in
   other place, where PATH variable is pointing or you feel like.

#. then modify pyGTKtalog line 6 to match right ``pygtktalog.py`` directory

Then, just run pyGTKtalog script.

Technical details
-----------------

Catalog file is plain sqlite database (optionally compressed with bzip2). All
images are stored in location pointed by db entry in ``config`` table - it is
assumed, that images directory will be placed within the root directory, where
the main db lies.
Generated sha512 hash from image file itself. There is small possibility for two
identical hash for different image files. However, no images are overwritten.
Thumbnail filename for each image is simply concatenation of image filename in
images directory and '_t' string.

There is also converter from old database to new for internal use only. In
public release there will be no other formats so it will be useless, and
deleted. There are some issues with converting. All thumbnails will be lost.
All images without big image will be lost. There are serious changes with
application design, and I decided, that is better to keep media unpacked on
disk, instead of pack it every time with save and unpack with open methods. New
design prevent from deleting any file from media directory (placed in
``~/.pygtktalog/images``). Functionality for exporting images and corresponding
db file is planned.


DEVELOPMENT
-----------

Several tools has been used to develop pyGTKtalog.

Paver
^^^^^

I've choose `Paver`_ as make equivalent. Inside main project directory there is
``pavement.py`` script, which provides several tasks, that can be helpful in a work
with sources. Paver is also used to generate standard ``setup.py``.

LICENSE
=======

This work is licensed under the terms of the GNU GPL, version 3. See the LICENCE
file in top-level directory.


.. _coverage: http://nedbatchelder.com/code/coverage/
.. _exif: https://github.com/ianare/exif-py
.. _gettext: http://www.gnu.org/software/gettext/gettext.html
.. _gthumb: http://gthumb.sourceforge.net
.. _gtktalog: http://www.nongnu.org/gtktalog/
.. _gwhere: http://www.gwhere.org/home.php3
.. _imagemagick: http://imagemagick.org/script/index.php
.. _intltool: http://www.gnome.org/
.. _mplayer: http://mplayerhq.hu
.. _nose: http://code.google.com/p/python-nose/
.. _paver: https://pythonhosted.org/paver/
.. _pil: http://www.pythonware.com/products/pil/index.htm
.. _pygtk 2.24: http://www.pygtk.org
.. _python 2.7: http://www.python.org/
.. _sqlalchemy 1.0: http://www.sqlalchemy.org
.. _tagging files: http://en.wikipedia.org/wiki/tag_%28metadata%29
.. _tox: https://testrun.org/tox
