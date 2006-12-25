# This Python file uses the following encoding: utf-8
# filetype = ('r','d')

import datetime
from pysqlite2 import dbapi2 as sqlite
import pygtk
import gtk
import gobject

class dbfile:
    def __init__(self,winobj,connection,cursor):
        self.con = connection
        self.cur = cursor
        self.winobj = winobj
        # create tree model
        self.dirmodel = self.treemodel=gtk.TreeStore(gobject.TYPE_INT, gobject.TYPE_STRING)
        self.filemodel = self.treemodel=gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING)
        
    def getDirectories(self,root=0):
        """get directory tree from DB"""
        
        self.cur.execute("select count(id) from files where type=1")
        self.count = self.cur.fetchone()[0]
        if self.count>0:
            frac = 1.0/self.count
        else:
            frac = 1.0
        self.count = 0

        if self.winobj.sbid != 0:
            self.winobj.status.remove(self.winobj.sbSearchCId, self.winobj.sbid)
        self.winobj.sbid = self.winobj.status.push(self.winobj.sbSearchCId, "Fetching data from catalog file")
            
        def get_children(id, name, parent):
            """fetch all children and place them in model"""
            #{{{
            myiter = self.dirmodel.insert_before(parent,None)
            self.dirmodel.set_value(myiter,0,id)
            self.dirmodel.set_value(myiter,1,name)
            self.cur.execute("SELECT o.child, f.filename FROM files_connect o LEFT JOIN files f ON o.child=f.id WHERE o.parent=? AND o.depth=1 AND f.type=1 ORDER BY f.filename",(id,))
            
            # progress
            self.winobj.progress.set_fraction(frac * self.count)
            while gtk.events_pending(): gtk.main_iteration()
            self.count = self.count + 1
            
            for cid,name in self.cur.fetchall():
                get_children(cid, name, myiter)
            #}}}
            
        # get initial roots from first, default root (id: 1) in the tree,
        # and then add other subroots to tree model
        if __debug__:
            data = datetime.datetime.now()
        self.cur.execute("SELECT o.child, f.filename FROM files_connect o LEFT JOIN files f ON o.child=f.id WHERE o.parent=1 AND o.depth=1 AND f.type=1 ORDER BY f.filename")
        
        # real volumes:
        for id,name in self.cur.fetchall():
            get_children(id,name,None)
        if __debug__:
            print "[db.py] tree generation time: ", (datetime.datetime.now() - data)
        
        if self.winobj.sbid != 0:
            self.winobj.status.remove(self.winobj.sbSearchCId, self.winobj.sbid)
        self.winobj.sbid = self.winobj.status.push(self.winobj.sbSearchCId, "Idle")
        
        self.winobj.progress.set_fraction(0)
            
        return self.dirmodel
    def getCurrentFiles(self,id):
        self.filemodel.clear()
        # parent for virtual '..' dir
        #myiter = self.filemodel.insert_before(None,None)
        #self.cur.execute("SELECT parent FROM files_connect WHERE child=? AND depth = 1",(id,))
        #self.filemodel.set_value(myiter,0,self.cur.fetchone()[0])
        #self.filemodel.set_value(myiter,1,'..')
        #if __debug__:
        #    print datetime.datetime.fromtimestamp(ch[3])
        
        # directories first
        self.cur.execute("SELECT o.child, f.filename, f.size, f.date FROM files_connect o LEFT JOIN files f ON o.child=f.id WHERE o.parent=? AND o.depth=1 AND f.type=1 ORDER BY f.filename",(id,))
        for ch in self.cur.fetchall():
            myiter = self.filemodel.insert_before(None,None)
            self.filemodel.set_value(myiter,0,ch[0])
            self.filemodel.set_value(myiter,1,ch[1])
            self.filemodel.set_value(myiter,2,ch[2])
            self.filemodel.set_value(myiter,3,datetime.datetime.fromtimestamp(ch[3]))
            self.filemodel.set_value(myiter,4,1)
            self.filemodel.set_value(myiter,5,'direktorja')
            #print datetime.datetime.fromtimestamp(ch[3])
            
        # all the rest
        self.cur.execute("SELECT o.child, f.filename, f.size, f.date, f.type FROM files_connect o LEFT JOIN files f ON o.child=f.id WHERE o.parent=? AND o.depth=1 AND f.type!=1 ORDER BY f.filename",(id,))
        for ch in self.cur.fetchall():
            myiter = self.filemodel.insert_before(None,None)
            self.filemodel.set_value(myiter,0,ch[0])
            self.filemodel.set_value(myiter,1,ch[1])
            self.filemodel.set_value(myiter,2,ch[2])
            self.filemodel.set_value(myiter,3,datetime.datetime.fromtimestamp(ch[3]))
            self.filemodel.set_value(myiter,4,ch[4])
            self.filemodel.set_value(myiter,5,'kategoria srategoria')
            #print datetime.datetime.fromtimestamp(ch[3])
        #self.filemodel.set_sort_func(1,self.sort_files_view)
        return self.filemodel
        
    def sort_files_view(self,a,b,c):
        print a,b,c
        return 2
