# This Python file uses the following encoding: utf-8
# filetype = ('r','d')

import datetime
from pysqlite2 import dbapi2 as sqlite

class dbfile:
    def __init__(self,db=None):
        if db !=None:
            self.con = sqlite.connect("%s" % db, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
            self.cur = self.con.cursor()
        else:
            name = datetime.datetime.now()
            name = "/tmp/pygtktalog%d.db" % name.microsecond
            self.con = sqlite.connect("%s" % name, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
            self.cur = self.con.cursor()
            self.createDB()
        pass
    def createDB(self):
        """make plain new database"""
        self.cur.execute("create table files(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, date timestamp, size integer, type integer)")
        self.cur.execute("create table files_connect(id INTEGER PRIMARY KEY AUTOINCREMENT, parent integer, child integer, depth integer)")
        
    def populate(self,fileobj):
        """add fileobject to database"""
        print "aa"
        def make_tree(obj,spc,parent=0,depth=0):
            """how about members?"""
            self.cur.execute("insert into files(filename,date,size,type) values (?,?,?,?)", (obj.name,obj.date,obj.size,obj.filetype))
            self.cur.execute("select seq from sqlite_sequence where name='files'")
            file_id = self.cur.fetchone()
            self.cur.execute("insert into files_connect(parent,child,depth) values(?,?,?) ",(file_id[0], file_id[0], 0))
            parent = parent + 1
            depth = depth + 1
            print obj.name, parent, depth
            for i in obj.members:
                if i.filetype == "d":
                    print "%s[%s]" % (spc, i.name)
                else:
                    print "%s%s" % (spc, i.name)
                make_tree(i,spc+".",parent,depth)
        make_tree(fileobj,".")
        return ""
