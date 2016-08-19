pyGTKtalog 1.0
==============

pyGTKtalog is Linux/FreeBSD program for indexing CD/DVD or directories on
filesystem. It is similar to gtktalog <http://www.nongnu.org/gtktalog/> or
gwhere <http://www.gwhere.org/home.php3>. There is no coincidence in name of
application, because it's meant to be replacement (in some way) for gtktalog,
which seems to be dead project for years.

WARNING!
========

This version is mostly outdated, full of bugs, and may eat your data! First
usable version (this is what you are looking at right now) was completed around
2009 year, but implementation was done much earlier. During that time GTK2 was
changed significantly several times, because of that couple of pyGTKtalog
functionalities goes bad.

The reason for keeping this branch is for history and for GUI to the new engine
which was rewritten couple of years ago and have only cli tool to manipulate
DBs.

In other words - pyGTKtalog version on this branch is safe for **view only**
your catalog database, while it may corrupt database or other files while trying
to create/update your databases in any way.

You have been warned.

The rest of the README file:

FEATURES
========

- scan for files in selected media
- get/generate thumbnails from EXIF and other images
- stores selected EXIF tags
- add/edit description and notes
- fetch comments for images made in gThumb <http://gthumb.sourceforge.net>
- add/remove unlimited images to any file or directory
- tagging files <http://en.wikipedia.org/wiki/Tag_%28metadata%29>
- and more :)

REQUIREMENTS
============

pyGTKtalog is written in python with following dependencies:

- python 2.4 or higher
- pygtk 2.10 or higher <http://www.pygtk.org>
- pysqlite2 <http://pysqlite.org/> (unnecessary, if python 2.5 is used)

Optional modules:

- PIL <http://www.pythonware.com/products/pil/index.htm> for image
  manipulation

Additional pyGTKtalog uses pygtkmvc <http://pygtkmvc.sourceforge.net> by
Roberto Cavada and EXIF module by Gene Cash (slightly updatetd to EXIF 2.2 by
me) which are included in sources.

pyGTKtalog extensively uses external programs in unix spirit, however there is
small possibility of using it Windows (probably with limitations) and quite
big possibility to run it on other sophisticated unix-like systems (i.e.
BeOS/ZETA/Haiku, QNX or MacOSX).

INSTALLATION
============

You don't have to install it if you don't want to. You can just change current
directory to pyGTKtalog and simply run:

./pyGTKtalog

That's it. Alternatively, if you like to put it in more system wide place, all
you have to do is:

- put pyGTKtalog directory into your destination of choice (/usr/local/share,
  /opt or ~/ is typical bet)
- copy pyGTKtalog shell script to /usr/bin, /usr/local/bin or in
  other place, where PATH variable is pointing or you feel like.
- then modify pyGTKtalog line 6 to match right pygtktalog.py directory

Then, just run pyGTKtalog script.

TODO
====

PyGTKtalog is still under heavy development, however there is small chance to
change structure of catalogs (and if it'll change, there will be transparent
function to update DB schema).

For version 1.0 there are no features to be done, just bug fixes.

There are still minor aims for versions 1.x to be done:
- consolidate popup-menus with edit menu
- add popup menu for directly removing tag from tag cloud
- implement advanced search

For version 2.0:
- Export/Import
- Icon grid in files view
- command line support: query, adding media to collection etc
- internationalization
- export to XLS
- user defined group of tags (represented by color in cloud tag)
- hiding specified files - configurable, like dot prefixed, config files and
  manually selected
- tests
- warning about existing image in media directory

Removed:
- filetypes handling (movies, images, archives, documents etc). Now it have
  common, unified external "plugin" system - simple text output from command
  line programs.
- anime/movie
		- title
		- alt title
		- type (anime movie, movie, anime oav, anime tv series, tv series, etc)
		- cover/images
		- genre
		- lang
		- sub lang
		- release date (from - to)
		- anidb link/imdb link
  Maybe in future versions. Now text file descriptions/notes and tags have to
  be enough for good and fast information search.

NOTES
=====

Catalog file is plain sqlite database (optionally compressed with bzip2). All
images are stored in ~/.pygtktalog/images directory. Names for images are
generated sha512 hash from image file itself. There is small possibility for two
identical hash for different image files. However, no images are overwritten.
Thumbnail filename for each image is simply concatenation of image filename in
images directory and '_t' string.

There is also converter from old database to new for internal use only. In
public release there will be no other formats so it will be useless, and
deleted. There are some issues with converting. All thumbnails will be lost. All
images without big image will be lost. There are serious changes with
application design, and I decided, that is better to keep media unpacked on
disk, instead of pack it every time with save and unpack with open methods. New
design prevent from deleting any file from media directory (placed in
~/.pygtktalog/images). Functionality for exporting images and corresponding db
file is planned.

LICENSE
=======

This work is licensed under the terms of the GNU GPL, version 3. See the LICENCE
file in top-level directory.