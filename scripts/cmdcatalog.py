#!/usr/bin/env python
"""
Fast and ugly CLI interface for pyGTKtalog
"""
import os
import sys
import errno
from argparse import ArgumentParser

from pygtktalog import scan
from pygtktalog import misc
from pygtktalog.dbobjects import File, Config
from pygtktalog.dbcommon import connect, Session

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def colorize(txt, color):
    """Pretty print with colors to console."""
    color_map = {"black": BLACK,
                 "red": RED,
                 "green": GREEN,
                 "yellow": YELLOW,
                 "blue": BLUE,
                 "magenta": MAGENTA,
                 "cyan": CYAN,
                 "white": WHITE}
    return COLOR_SEQ % color_map[color] + txt + RESET_SEQ


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
            scan.LOG.setLevel("DEBUG")

    def _resolve_path(self, path):
        """Identify path in the DB"""
        if not path.startswith("/"):
            raise AttributeError("Path have to start with slash (/)")

        last_node = self.root
        for part in path.split("/"):
            if not part.strip():
                continue

            for node in last_node.children:
                if node.filename == part:
                    last_node = node
                    break
            else:
                raise AttributeError("No such path: %s" % path)

        return last_node

    def _make_path(self, node):
        """Make the path to the item in the DB"""
        if node.parent == node:
            return "/"

        ext = ""
        if node.parent.type == 0:
            ext = colorize(" (%s)" % node.filepath, "white")

        path = []
        path.append(node.filename)
        while node.parent != self.root:
            path.append(node.parent.filename)
            node = node.parent

        return "/".join([""] + path[::-1]) + ext

    def _walk(self, dirnode):
        """Recursively go through the leaves of the node"""
        items = []
        for node in dirnode.children:
            if node.type == 1:
                items += self._walk(node)

            items.append(" " + self._make_path(node))

        items.sort()
        return items

    def _list(self, node):
        """List only current node content"""
        items = []
        for node in node.children:
            if node != self.root:
                items.append(" " + self._make_path(node))

        items.sort()
        return items

    def close(self):
        """Close the session"""
        self.sess.commit()
        self.sess.close()

    def list(self, path=None, recursive=False):
        """Simulate ls command for the provided item path"""
        self.root = self.sess.query(File).filter(File.type==0).first()
        if path:
            node = self._resolve_path(path)
            msg = "Content of path `%s':" % path
        else:
            node = self.root
            msg = "Content of path `/':"

        print colorize(msg, "white")

        if recursive:
            items = self._walk(node)
        else:
            items = self._list(node)

        print "\n".join(items)

    def update(self, path, dir_to_update=None):
        """
        Update the DB against provided path and optionally directory on the
        real filesystem
        """
        self.root = self.sess.query(File).filter(File.type==0).first()
        node = self._resolve_path(path)
        if node == self.root:
            print colorize("Cannot update entire db, since root was provided "
                           "as path.", "red")
            return

        if not dir_to_update:
            dir_to_update = os.path.join(node.filepath, node.filename)

        if not os.path.exists(dir_to_update):
            raise OSError("Path to updtate doesn't exists: %s", dir_to_update)

        print colorize("Updating node `%s' against directory "
                       "`%s'" % (path, dir_to_update), "white")
        if not self.dry_run:
            scanob = scan.Scan(dir_to_update)
            # scanob.update_files(node.id)
            scanob.update_files(node.id, self.engine)

    def create(self, dir_to_add, data_dir):
        """Create new database"""
        self.root = File()
        self.root.id = 1
        self.root.filename = 'root'
        self.root.size = 0
        self.root.source = 0
        self.root.type = 0
        self.root.parent_id = 1

        config = Config()
        config.key = "image_path"
        config.value = data_dir

        if not self.dry_run:
            self.sess.add(self.root)
            self.sess.add(config)
            self.sess.commit()

        print colorize("Creating new db against directory `%s'" % dir_to_add,
                       "white")
        if not self.dry_run:
            if data_dir == ":same_as_db:":
                misc.calculate_image_path(None, True)
            else:
                misc.calculate_image_path(data_dir, True)

            scanob = scan.Scan(dir_to_add)
            scanob.add_files(self.engine)

    def add(self, dir_to_add):
        """Add new directory to the db"""
        self.root = self.sess.query(File).filter(File.type==0).first()

        if not os.path.exists(dir_to_add):
            raise OSError("Path to add doesn't exists: %s", dir_to_add)

        print colorize("Adding directory `%s'" % dir_to_add, "white")
        if not self.dry_run:
            scanob = scan.Scan(dir_to_add)
            scanob.add_files()


def list_db(args):
    """List"""
    if not os.path.exists(args.db):
        print colorize("File `%s' does not exists!" % args.db, "red")
        sys.exit(1)

    obj = Iface(args.db, False, args.debug)
    obj.list(path=args.path, recursive=args.recursive)
    obj.close()


def update_db(args):
    """Update"""
    if not os.path.exists(args.db):
        print colorize("File `%s' does not exists!" % args.db, "red")
        sys.exit(1)

    obj = Iface(args.db, args.pretend, args.debug)
    obj.update(args.path, dir_to_update=args.dir_to_update)
    obj.close()


def add_dir(args):
    """Add"""
    if not os.path.exists(args.db):
        print colorize("File `%s' does not exists!" % args.db, "red")
        sys.exit(1)

    obj = Iface(args.db, args.pretend, args.debug)
    obj.add(args.dir_to_add)
    obj.close()


def create_db(args):
    """List"""
    if os.path.exists(args.db):
        print colorize("File `%s' exists!" % args.db, "yellow")

    obj = Iface(args.db, args.pretend, args.debug)
    obj.create(args.dir_to_add, args.imagedir)
    obj.close()


def main():
    """Main"""
    parser = ArgumentParser()

    subparser = parser.add_subparsers()
    list_ = subparser.add_parser("list")
    list_.add_argument("db")
    list_.add_argument("path", nargs="?")
    list_.add_argument("-r", "--recursive", help="list items in "
                       "subdirectories", action="store_true", default=False)
    list_.add_argument("-d", "--debug", help="Turn on debug",
                       action="store_true", default=False)
    list_.set_defaults(func=list_db)

    update = subparser.add_parser("update")
    update.add_argument("db")
    update.add_argument("path")
    update.add_argument("dir_to_update", nargs="?")
    update.add_argument("-p", "--pretend", help="Don't do the action, just "
                        "give the info what would gonna to happen.",
                        action="store_true", default=False)
    update.add_argument("-d", "--debug", help="Turn on debug",
                        action="store_true", default=False)
    update.set_defaults(func=update_db)

    create = subparser.add_parser("create")
    create.add_argument("db")
    create.add_argument("dir_to_add")
    create.add_argument("-i", "--imagedir", help="Directory where to put "
                        "images for the database. Popular, but deprecated "
                        "choice is  `~/.pygtktalog/images'. Currnet default "
                        "is special string `:same_as_db:' which will try to "
                        "create directory with the same name as the db with "
                        "data suffix", default=":same_as_db:")
    create.add_argument("-p", "--pretend", help="Don't do the action, just "
                        "give the info what would gonna to happen.",
                        action="store_true", default=False)
    create.add_argument("-d", "--debug", help="Turn on debug",
                        action="store_true", default=False)
    create.set_defaults(func=create_db)

    add = subparser.add_parser("add")
    add.add_argument("db")
    add.add_argument("dir_to_add")
    add.add_argument("-p", "--pretend", help="Don't do the action, just "
                     "give the info what would gonna to happen.",
                     action="store_true", default=False)
    add.add_argument("-d", "--debug", help="Turn on debug",
                     action="store_true", default=False)
    add.set_defaults(func=add_dir)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
