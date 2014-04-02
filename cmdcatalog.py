#!/usr/bin/env python
import os
import sys
from argparse import ArgumentParser

from pygtktalog import scan
from pygtktalog.dbobjects import File
from pygtktalog.dbcommon import connect, Session

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def cprint(txt, color):
    color_map = {"black": BLACK,
                 "red": RED,
                 "green": GREEN,
                 "yellow": YELLOW,
                 "blue": BLUE,
                 "magenta": MAGENTA,
                 "cyan": CYAN,
                 "white": WHITE}
    print COLOR_SEQ % (30 + color_map[color]) + txt + RESET_SEQ


class Iface(object):
    def __init__(self, dbname, pretend=False, debug=False):
        self.engine = connect(dbname)
        self.sess = Session()
        self.dry_run = pretend
        self.root = None
        if debug:
            scan.LOG.setLevel("DEBUG")

    def close(self):
        self.sess.commit()
        self.sess.close()

    # def create(self):
        # self.sess.commit()
        # self.sess.close()

    def _resolve_path(self, path):
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
        if node.parent == node:
            return "/"

        path = []
        path.append(node.filename)
        while node.parent != self.root:
            path.append(node.parent.filename)
            node = node.parent

        return "/".join([""] + path[::-1])

    def list(self, path=None):
        self.root = self.sess.query(File).filter(File.type==0).first()
        if path:
            node = self._resolve_path(path)
            msg = "Content of path `%s':" % path
        else:
            node = self.root
            msg = "Content of path `/':"

        cprint(msg, "white")
        for node in node.children:
            if node != self.root:
                #if __debug__:
                #    print "  %d:" % node.id, self._make_path(node)
                #else:
                print " ", self._make_path(node)

    def update(self, path, dir_to_update=None):
        self.root = self.sess.query(File).filter(File.type==0).first()
        node = self._resolve_path(path)
        if node == self.root:
            cprint("Cannot update entire db, since root was provided as path.",
                   "red")
            return

        if not dir_to_update:
            dir_to_update = os.path.join(node.filepath, node.filename)

        if not os.path.exists(dir_to_update):
            raise OSError("Path to updtate doesn't exists: %s", dir_to_update)

        cprint("Updating node `%s' against directory "
               "`%s'" % (path, dir_to_update), "white")
        if not self.dry_run:
            scanob = scan.Scan(dir_to_update)
            # scanob.update_files(node.id)
            scanob.update_files(node.id, self.engine)

    def create(self, dir_to_add):
        self.root = File()
        self.root.id = 1
        self.root.filename = 'root'
        self.root.size = 0
        self.root.source = 0
        self.root.type = 0
        self.root.parent_id = 1
        if not self.dry_run:
            self.sess.add(self.root)
            self.sess.commit()

        cprint("Creating new db against directory `%s'" % dir_to_add, "white")
        if not self.dry_run:
            scanob = scan.Scan(dir_to_add)
            scanob.add_files(self.engine)


def list_db(args):
    if not os.path.exists(args.db):
        cprint("File `%s' does not exists!" % args.db, "red")
        sys.exit(1)

    obj = Iface(args.db, False, args.debug)
    obj.list(path=args.path)
    obj.close()


def update_db(args):
    if not os.path.exists(args.db):
        cprint("File `%s' does not exists!" % args.db, "red")
        sys.exit(1)

    obj = Iface(args.db, args.pretend, args.debug)
    obj.update(args.path, dir_to_update=args.dir_to_update)
    obj.close()

def create_db(args):
    if os.path.exists(args.db):
        cprint("File `%s' exists!" % args.db, "yellow")

    obj = Iface(args.db, args.pretend, args.debug)
    obj.create(args.dir_to_add)
    obj.close()


if __name__ == "__main__":
    parser = ArgumentParser()

    subparser = parser.add_subparsers()
    list_ = subparser.add_parser("list")
    list_.add_argument("db")
    list_.add_argument("path", nargs="?")
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
    create.add_argument("-p", "--pretend", help="Don't do the action, just "
                        "give the info what would gonna to happen.",
                        action="store_true", default=False)
    create.add_argument("-d", "--debug", help="Turn on debug",
                        action="store_true", default=False)
    create.set_defaults(func=create_db)

    args = parser.parse_args()
    args.func(args)


"""
db_file = "/home/gryf/spisy/xxx.sqlite"
connect(db_file)
sess = Session()

#if not sess.query(File).get(1):
#    root = File()
#    root.id = 1
#    root.filename = 'root'
#    root.size = 0
#    root.source = 0
#    t.type = 0
#    root.parent_id = 1
#    sess.add(root)
#    sess.commit()

f = "/mnt/hardtwo/XXX/"
scanob = scan.Scan(f)
scanob.update_files(2)
"""
