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
        self.filemodel = self.treemodel=gtk.TreeStore(gobject.TYPE_INT, gobject.TYPE_STRING,gobject.TYPE_STRING)
        
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
            myiter = self.dirmodel.insert_after(parent,None)
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
        
