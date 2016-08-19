pyGTKtalog
==========

pyGTKtalog is Linux/FreeBSD program for indexing CD/DVD or directories on
filesystem. It is similar to `gtktalog <http://www.nongnu.org/gtktalog/>`_ or
`gwhere <http://www.gwhere.org/home.php3>`_. There is no coincidence in name of
application, because it's meant to be replacement (in some way) for gtktalog,
which seems to be dead project for years.

Current version is 1.9.

FEATURES
--------

* scan for files in selected media
* get/generate thumbnails from exif and other images
* most important exif tags
* add/edit description and notes
* fetch comments for images made in `gThumb <http://gthumb.sourceforge.net>`_
* add/remove unlimited images to any file or directory
* `tagging files <http://en.wikipedia.org/wiki/Tag_%28metadata%29>`_
* and more :)

REQUIREMENTS
------------

pyGTKtalog requires python and following libraries:

* `python 2.6 <http://www.python.org/>`_
* `pygtk 2.16 <http://www.pygtk.org>`_
* `pygtkmvc 1.99 <http://sourceforge.net/apps/trac/pygtkmvc/wiki>`_
* `sqlalchemy 0.6 <http://www.sqlalchemy.org>`_

It may work on other (lower) version of libraries, and it should work with
higher versions of libraries.

.. note::

    Although pygtkmvc is `listed on pypi
    <http://pypi.python.org/pypi/python-gtkmvc/>`_ it may happen that you
    have to download it directly from
    `sourceforge <http://sourceforge.net/apps/trac/pygtkmvc/wiki>`_ page and
    install manually. I don't know about pygtk (I've installed it by my
    system package manager), but all the others python libraries (sqlalchemy,
    paver, nose, coverage) should be installable via `pip
    <http://pypi.python.org/pypi/pip>`_

Optional modules
^^^^^^^^^^^^^^^^

* `PIL <http://www.pythonware.com/products/pil/index.htm>`_ for image manipulation

Additional pyGTKtalog uses EXIF module by Gene Cash (slightly updated to EXIF
2.2 by me) which is included in sources.

pyGTKtalog extensively uses external programs in unix spirit, however there is
small possibility of using it Windows (probably with limitations) and quite big
possibility to run it on other sophisticated unix-like systems (i.e.
BeOS/ZETA/Haiku, QNX or MacOSX).

Programs that are used:
* mencoder (provided by mplayer package)
* montage, convert from ImageMagick

For development process following programs are used:

* `gettext <http://www.gnu.org/software/gettext/gettext.html>`_
* `intltool <http://www.gnome.org/>`_
* `nose <http://code.google.com/p/python-nose/>`_
* `coverage <http://nedbatchelder.com/code/coverage/>`_
* `paver <http://code.google.com/p/paver/>`__

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

#. then modify pyGTKtalog line 6 to match right pygtktalog.py directory

Then, just run pyGTKtalog script.

TODO
----

PyGTKtalog is still under heavy development, however there is small chance to
change structure of catalogs (and if it'll change, there will be transparent
function to update DB schema).

For version 1.0 there are no features to be done, just bug fixes.

There are still minor aims for versions 1.x to be done:

* consolidate popup-menus with edit menu
* add popup menu for directly removing tag from tag cloud
* implement advanced search

For version 2.0:

* Export/Import
* Icon grid in files view
* command line support: query, adding media to collection etc
* internationalization
* export to XLS
* user defined group of tags (represented by color in cloud tag)
* hiding specified files - configurable, like dot prefixed, config and
  manually selected
* tests
* warning about existing image in media directory

Removed:

* filetypes handling (movies, images, archives, documents etc). Now it have
  common, unified external "plugin" system - simple text output from command
  line programs.
* anime/movie
    * title
    * alt title
    * type (anime movie, movie, anime oav, anime tv series, tv series, etc)
    * cover/images
    * genre
    * lang
    * sub lang
    * release date (from - to)
    * anidb link/imdb link

Maybe in future versions. Now text file descriptions/notes and tags have to
be enough for good and fast information search.

NOTES
-----

Catalog file is plain sqlite database (optionally compressed with bzip2). All
images are stored in ``~/.pygtktalog/images`` directory. Names for images are
generated sha512 hash from image file itself. There is small possibility for two
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

I've choose `Paver <http://www.blueskyonmars.com/projects/paver/>`_ as make
equivalent. Inside main project directory there is pavement.py script, which
provides several tasks, that can be helpful in a work with sources. Paver is
also used to generate standard setup.py.

LICENSE
=======

This work is licensed under the terms of the GNU GPL, version 3. See the LICENCE
file in top-level directory.
