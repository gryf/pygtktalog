#!/usr/bin/env python
"""
Fast and ugly CLI interface for pyGTKtalog
"""
import argparse
import os
import re
import sys

from sqlalchemy import or_

from pygtktalog import scan
from pygtktalog import misc
from pygtktalog import dbobjects as dbo
from pygtktalog.dbcommon import connect, Session
from pygtktalog import logger

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)

RESET_SEQ = '\033[0m'
COLOR_SEQ = '\033[1;%dm'
BOLD_SEQ = '\033[1m'

LOG = logger.get_logger(__name__)


def colorize(txt, color):
    """Pretty print with colors to console."""
    color_map = {'black': BLACK,
                 'red': RED,
                 'green': GREEN,
                 'yellow': YELLOW,
                 'blue': BLUE,
                 'magenta': MAGENTA,
                 'cyan': CYAN,
                 'white': WHITE}
    return COLOR_SEQ % color_map[color] + txt + RESET_SEQ


def asserdb(func):
    def wrapper(args):
        if not os.path.exists(args.db):
            print(colorize("File `%s' does not exists!" % args.db, 'red'))
            sys.exit(1)
        func(args)
    return wrapper


TYPE_MAP = {0: 'd', 1: 'd', 2: 'f', 3: 'l'}


class Iface(object):
    """Main class which interacts with the pyGTKtalog modules"""
    def __init__(self, dbname, pretend=False, debug=False):
        """Init"""
        self.engine = connect(dbname)
        self.sess = Session()
        self.dry_run = pretend
        self.root = None
        self._dbname = dbname
        if debug:
            scan.LOG.setLevel('DEBUG')
            LOG.setLevel('DEBUG')

    def _resolve_path(self, path):
        """Identify path in the DB"""
        if not path.startswith("/"):
            raise AttributeError('Path have to start with slash (/)')

        last_node = self.root
        for part in path.split('/'):
            if not part.strip():
                continue

            for node in last_node.children:
                if node.filename == part:
                    last_node = node
                    break
            else:
                raise AttributeError('No such path: %s' % path)

        return last_node

    def _get_full_path(self, file_object):
        """given the file object, return string with full path to it"""
        parent = file_object.parent
        path = [file_object.filename]

        while parent.type:
            path.insert(0, parent.filename)
            parent = parent.parent

        return u'/' + u'/'.join(path)

    def _make_path(self, node):
        """Make the path to the item in the DB"""
        orig_node = node
        if node.parent == node:
            return {u'/': (u' ', 0, u' ')}

        ext = ''
        if node.parent.type == dbo.TYPE['root']:
            ext = colorize(' (%s)' % node.filepath, 'white')

        path = []
        path.append(node.filename)
        while node.parent != self.root:
            path.append(node.parent.filename)
            node = node.parent

        path = '/'.join([''] + path[::-1]) + ext

        return {path: (TYPE_MAP[orig_node.type],
                       orig_node.size,
                       orig_node.date)}

    def _walk(self, dirnode):
        """Recursively go through the leaves of the node"""
        items = {}

        for node in dirnode.children:
            if node.type == dbo.TYPE['dir']:
                items.update(self._walk(node))

            items.update(self._make_path(node))

        return items

    def _list(self, node):
        """List only current node content"""
        items = {}
        for node in node.children:
            if node != self.root:
                items.update(self._make_path(node))

        return items

    def close(self):
        """Close the session"""
        self.sess.commit()
        self.sess.close()

    def list(self, path=None, recursive=False, long_=False):
        """Simulate ls command for the provided item path"""
        self.root = self.sess.query(dbo.File)
        self.root = self.root.filter(dbo.File.type == dbo.TYPE['root']).first()
        if path:
            node = self._resolve_path(path)
            msg = "Content of path `%s':" % path
        else:
            node = self.root
            msg = "Content of path `/':"

        print(colorize(msg, 'white'))

        if recursive:
            items = self._walk(node)
        else:
            items = self._list(node)

        if long_:
            filenames = []
            format_str = (u'{} {:>%d,} {} {}' %
                          _get_highest_size_length(items))
            for fname in sorted(items.keys()):
                type_, size, date = items[fname]
                filenames.append(format_str.format(type_, size, date, fname))
        else:
            filenames = sorted(items.keys())

        print('\n'.join(filenames))

    def update(self, path, dir_to_update=None):
        """
        Update the DB against provided path and optionally directory on the
        real filesystem
        """
        self.root = self.sess.query(dbo.File)
        self.root = self.root.filter(dbo.File.type == dbo.TYPE['root']).first()
        node = self._resolve_path(path)
        if node == self.root:
            print(colorize('Cannot update entire db, since root was provided '
                           'as path.', 'red'))
            return

        if not dir_to_update:
            dir_to_update = os.path.join(node.filepath, node.filename)

        if not os.path.exists(dir_to_update):
            raise OSError("Path to updtate doesn't exists: %s", dir_to_update)

        print(colorize("Updating node `%s' against directory "
                       "`%s'" % (path, dir_to_update), 'white'))
        if not self.dry_run:
            scanob = scan.Scan(dir_to_update)
            # scanob.update_files(node.id)
            scanob.update_files(node.id, self.engine)

    def create(self, dir_to_add, data_dir):
        """Create new database"""
        self.root = dbo.File()
        self.root.id = 1
        self.root.filename = 'root'
        self.root.size = 0
        self.root.source = 0
        self.root.type = 0
        self.root.parent_id = 1

        config = dbo.Config()
        config.key = 'image_path'
        config.value = data_dir

        if not self.dry_run:
            self.sess.add(self.root)
            self.sess.add(config)
            self.sess.commit()

        print(colorize("Creating new db against directory `%s'" % dir_to_add,
                       'white'))
        if not self.dry_run:
            if data_dir == ':same_as_db:':
                misc.calculate_image_path(None, True)
            else:
                misc.calculate_image_path(data_dir, True)

            scanob = scan.Scan(dir_to_add)
            scanob.add_files(self.engine)

    def add(self, dir_to_add):
        """Add new directory to the db"""
        self.root = self.sess.query(dbo.File)
        self.root = self.root.filter(dbo.File.type == 0).first()

        if not os.path.exists(dir_to_add):
            raise OSError("Path to add doesn't exists: %s", dir_to_add)

        print(colorize("Adding directory `%s'" % dir_to_add, 'white'))
        if not self.dry_run:
            scanob = scan.Scan(dir_to_add)
            scanob.add_files()

    def _annotate(self, item, search_words):
        """
        Find ranges to be highlighted in item, provide them and return result
        string
        """
        indexes = []
        for word in search_words:
            for match in re.finditer(re.escape(word.lower()), item.lower()):
                for index in range(match.start(), match.end()):
                    indexes.append(index)

        highlight = False
        result = []

        for idx, char in enumerate(item):
            if idx in indexes:
                if not highlight:
                    highlight = True
                    result.append(COLOR_SEQ % WHITE)
                result.append(char)
            else:
                if highlight:
                    highlight = False
                    result.append(RESET_SEQ)
                result.append(char)

        return "".join(result)

    def find(self, search_words):
        query = self.sess.query(dbo.File).filter(or_(dbo.File.type == 2,
                                                     dbo.File.type == 3))
        result = []

        for word in search_words:
            phrase = u'%%%s%%' % word
            query = query.filter(dbo.File.filename.like(phrase))

        for item in query.all():
            result.append(self._get_full_path(item))

        if not result:
            print("No results for `%s'" % ' '.join(search_words))
            return

        result.sort()
        for item in result:
            print(self._annotate(item, search_words))

    def fsck(self):
        """Fsck orphaned images/thumbs"""
        image_path = (self.sess.query(dbo.Config)
                      .filter(dbo.Config.key == 'image_path')).one().value

        if image_path == ':same_as_db:':
            image_path = misc.calculate_image_path(None, False)

        files_to_remove = []

        # remove images/thumbnails which doesn't have file relation
        for name, obj in (("images", dbo.Image),
                          ("thumbnails", dbo.Thumbnail)):
            self._purge_orphaned_objects(obj, "Scanning %s " % name)

        # find all image files not associate with either Image (image/thumb)
        # or Thumbnail (thumb) objects
        sys.stdout.write(40 * " " + "\r")
        count = 0
        for root, dirs, files in os.walk(image_path):
            for fname in files:
                sys.stdout.write("Scanning files " +
                                 "| / - \\".split()[count % 4] + "\r")
                sys.stdout.flush()
                count += 1

                fname_ = os.path.join(root.split(image_path)[1],
                                      fname).lstrip('/')

                if '_t' in fname:
                    obj = (self.sess.query(dbo.Thumbnail)
                           .filter(dbo.Thumbnail.filename == fname_)).all()
                    if obj:
                        continue

                    obj = (self.sess.query(dbo.Image)
                           .filter(dbo.Image.filename ==
                                   fname_.replace('_t.', '.'))).all()
                    if obj:
                        continue

                else:
                    obj = (self.sess.query(dbo.Image)
                           .filter(dbo.Image.filename == fname_)).all()
                    if obj:
                        continue

                files_to_remove.append(os.path.join(root, fname))

        LOG.debug("Found %d orphaned files", len(files_to_remove))
        sys.stdout.write(40 * " " + "\r")
        sys.stdout.flush()

        if self.dry_run:
            print("Following files are not associated to any items in the DB:")
            for filename in sorted(files_to_remove):
                print(filename)
            self.sess.rollback()
        else:
            _remove_files(image_path, files_to_remove)
            self.sess.commit()

    def _purge_orphaned_objects(self, sa_class, msg):
        """Return tuple of lists of images that are orphaned"""

        ids_to_remove = []

        for count, item in enumerate(self.sess.query(sa_class).all()):
            sys.stdout.write(msg + "| / - \\".split()[count % 4] + "\r")
            if not item.file:
                self.sess.delete(item)
                ids_to_remove.append(item.id)
                del item
            sys.stdout.flush()

        LOG.debug("Found %d orphaned object of class %s",
                  len(ids_to_remove), sa_class.__name__)
        self.sess.flush()


def _remove_files(image_path, filenames):
    """Remove files and empty directories in provided location"""

    count = 0
    for count, fname in enumerate(filenames, start=1):
        os.unlink(fname)

    LOG.info("Removed %d orphaned files", count)

    count = 0
    for root, dirs, _ in os.walk(image_path):
        for dirname in dirs:
            try:
                os.rmdir(os.path.join(root, dirname))
                count += 1
            except OSError:
                pass
    LOG.info("Removed %d empty directories", count)


def _get_highest_size_length(item_dict):
    highest = len(str(sorted([i[1] for i in item_dict.values()])[-1]))
    return highest + highest / 3


@asserdb
def list_db(args):
    """List"""
    obj = Iface(args.db, False, args.debug)
    obj.list(path=args.path, recursive=args.recursive, long_=args.long)
    obj.close()


@asserdb
def update_db(args):
    """Update"""
    obj = Iface(args.db, args.pretend, args.debug)
    obj.update(args.path, dir_to_update=args.dir_to_update)
    obj.close()


@asserdb
def add_dir(args):
    """Add"""
    obj = Iface(args.db, args.pretend, args.debug)
    obj.add(args.dir_to_add)
    obj.close()


def create_db(args):
    """List"""
    obj = Iface(args.db, args.pretend, args.debug)
    obj.create(args.dir_to_add, args.imagedir)
    obj.close()


@asserdb
def search(args):
    """Find"""
    obj = Iface(args.db, False, args.debug)
    obj.find(args.search_words)
    obj.close()


@asserdb
def cleanup(args):
    """Cleanup"""
    obj = Iface(args.db, False, args.debug)
    obj.fsck()
    obj.close()


def main():
    """Main"""
    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers()
    list_ = subparser.add_parser('list')
    list_.add_argument('db')
    list_.add_argument('path', nargs='?')
    list_.add_argument('-l', '--long', help='Show size, date and type',
                       action='store_true', default=False)
    list_.add_argument('-r', '--recursive', help='list items in '
                       'subdirectories', action='store_true', default=False)
    list_.add_argument('-d', '--debug', help='Turn on debug',
                       action='store_true', default=False)
    list_.set_defaults(func=list_db)

    update = subparser.add_parser('update')
    update.add_argument('db')
    update.add_argument('path')
    update.add_argument('dir_to_update', nargs='?')
    update.add_argument('-p', '--pretend', help="Don't do the action, just "
                        "give the info what would gonna to happen.",
                        action='store_true', default=False)
    update.add_argument('-d', '--debug', help='Turn on debug',
                        action='store_true', default=False)
    update.set_defaults(func=update_db)

    create = subparser.add_parser('create')
    create.add_argument('db')
    create.add_argument('dir_to_add')
    create.add_argument('-i', '--imagedir', help="Directory where to put "
                        "images for the database. Popular, but deprecated "
                        "choice is  `~/.pygtktalog/images'. Current default "
                        "is special string `:same_as_db:' which will try to "
                        "create directory with the same name as the db with "
                        "data suffix", default=':same_as_db:')
    create.add_argument('-p', '--pretend', help="Don't do the action, just "
                        "give the info what would gonna to happen.",
                        action='store_true', default=False)
    create.add_argument('-d', '--debug', help='Turn on debug',
                        action='store_true', default=False)
    create.set_defaults(func=create_db)

    add = subparser.add_parser('add')
    add.add_argument('db')
    add.add_argument('dir_to_add')
    add.add_argument('-p', '--pretend', help="Don't do the action, just "
                     "give the info what would gonna to happen.",
                     action='store_true', default=False)
    add.add_argument('-d', '--debug', help='Turn on debug',
                     action='store_true', default=False)
    add.set_defaults(func=add_dir)

    find = subparser.add_parser('find')
    find.add_argument('db')
    find.add_argument('search_words', nargs='+')
    find.add_argument('-d', '--debug', help='Turn on debug',
                      action='store_true', default=False)
    find.set_defaults(func=search)

    fsck = subparser.add_parser('fsck')
    fsck.add_argument('db')
    fsck.add_argument('-p', '--pretend', help="Don't do the action, just give"
                      " the info what would gonna to happen.",
                      action='store_true', default=False)
    fsck.add_argument('-d', '--debug', help='Turn on debug',
                      action='store_true', default=False)
    fsck.set_defaults(func=cleanup)

    args = parser.parse_args()

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
