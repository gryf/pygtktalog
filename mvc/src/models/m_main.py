# This Python file uses the following encoding: utf-8

import utils._importer
import utils.globals
from gtkmvc.model_mt import ModelMT

try:
    import threading as _threading
except ImportError:
    if __debug__:
        print "import exception: _threading"
    import dummy_threading as _threading

from pysqlite2 import dbapi2 as sqlite
import datetime
import mx.DateTime
import os
import mimetypes

import gtk
import gobject

from m_config import ConfigModel

class MainModel(ModelMT):
    """Create, load, save, manipulate db file which is container for our data"""
    
    __properties__ = {'busy': False, 'statusmsg': '', 'progress': 0}
    
    config = ConfigModel()
    unsaved_project = False
    filename = None
    internal_filename = None
    modified = False
    db_connection = None
    db_cursor = None
    abort = False
    discsTree = gtk.TreeStore(gobject.TYPE_INT, gobject.TYPE_STRING,str)
    filesList = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING,str)
    
    def __init__(self):
        ModelMT.__init__(self)
        self.config.load()
        return
        
    def cleanup(self):
        self.__close_db_connection()
        if self.internal_filename != None:
            try:
                os.unlink(self.internal_filename)
            except:
                if __debug__:
                    print "m_db.py: 31"
                    print self.internal_filename
                pass
            try:
                os.unlink(self.internal_filename + '-journal')
            except:
                if __debug__:
                    print "m_db.py: 38"
                    print self.internal_filename+'-journal'
                pass
        return
        
    def load(self):
        pass
        
    def new(self):
        self.modified = False
        self.__create_internal_filename()
        self.__connect_to_db()
        self.__create_database()
        
        try:
            self.discsTree.clear()
        except:
            pass
            
        try:
            self.filesList.clear()
        except:
            pass
        
        return
        
    def save(self):
        return
        
    def scan(self,path,label):
        """scan files in separated thread"""
        
        # flush buffer to release db lock.
        self.db_connection.commit()
        
        self.path = path
        self.label = label
        
        if self.busy:
            return
        self.thread = _threading.Thread(target=self.__scan)
        self.thread.start()
        return
        
    def refresh_tree(self):
        """generate tree model from discs tree"""
        if __debug__:
            print "refreshing"
        # flush buffer to release db lock.
        self.db_connection.commit()
        
        if self.busy:
            return
        self.thread = _threading.Thread(target=self.__prepare_discs_treemodel)
        self.thread.start()
        
        return
        
    def get_root_entries(self,id=None):
        try:
            self.filesList.clear()
        except:
            pass
        # parent for virtual '..' dir
        #myiter = self.filemodel.insert_before(None,None)
        #self.cur.execute("SELECT parent FROM files_connect WHERE child=? AND depth = 1",(id,))
        #self.filemodel.set_value(myiter,0,self.cur.fetchone()[0])
        #self.filemodel.set_value(myiter,1,'..')
        #if __debug__:
        #    print datetime.datetime.fromtimestamp(ch[3])
        
        # directories first
        self.db_cursor.execute("SELECT o.child, f.filename, f.size, f.date FROM files_connect o LEFT JOIN files f ON o.child=f.id WHERE o.parent=? AND o.depth=1 AND f.type=1 ORDER BY f.filename",(id,))
        for ch in self.db_cursor.fetchall():
            myiter = self.filesList.insert_before(None,None)
            self.filesList.set_value(myiter,0,ch[0])
            self.filesList.set_value(myiter,1,ch[1])
            self.filesList.set_value(myiter,2,ch[2])
            self.filesList.set_value(myiter,3,datetime.datetime.fromtimestamp(ch[3]))
            self.filesList.set_value(myiter,4,1)
            self.filesList.set_value(myiter,5,'direktorja')
            self.filesList.set_value(myiter,6,gtk.STOCK_DIRECTORY)
            #print datetime.datetime.fromtimestamp(ch[3])
            
        # all the rest
        self.db_cursor.execute("SELECT o.child, f.filename, f.size, f.date, f.type FROM files_connect o LEFT JOIN files f ON o.child=f.id WHERE o.parent=? AND o.depth=1 AND f.type!=1 ORDER BY f.filename",(id,))
        for ch in self.db_cursor.fetchall():
            myiter = self.filesList.insert_before(None,None)
            self.filesList.set_value(myiter,0,ch[0])
            self.filesList.set_value(myiter,1,ch[1])
            self.filesList.set_value(myiter,2,ch[2])
            self.filesList.set_value(myiter,3,datetime.datetime.fromtimestamp(ch[3]))
            self.filesList.set_value(myiter,4,ch[4])
            self.filesList.set_value(myiter,5,'kategoria srategoria')
            self.filesList.set_value(myiter,6,gtk.STOCK_FILE)
            #print datetime.datetime.fromtimestamp(ch[3])
        return
        
    def get_file_info(self,id):
        """get file info from database"""
        self.db_cursor.execute("SELECT filename, date, size, type FROM files WHERE id = ?",(id,))
        set = self.db_cursor.fetchone()
        if set == None:
            return ''
            
        string = """Filename: %s
Date: %s
Size: %s
type: %s""" % (set[0],datetime.datetime.fromtimestamp(set[1]),set[2],set[3])
        return string
        
    # private class functions
    def __connect_to_db(self):
        self.db_connection = sqlite.connect("%s" % self.internal_filename, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.db_cursor = self.db_connection.cursor()
        return
    
    def __close_db_connection(self):
        if self.db_cursor != None:
            self.db_cursor.close()
        if self.db_connection != None:
            self.db_connection.close()
        return
        
    def __create_internal_filename(self):
        self.cleanup()
        self.internal_filename = "/tmp/pygtktalog%d.db" % datetime.datetime.now().microsecond
        return
    
    def __compress(self):
        return
    
    def __create_database(self):
        """make all necessary tables in db file"""
        self.db_cursor.execute("create table files(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, date datetime, size integer, type integer);")
        self.db_cursor.execute("create table files_connect(id INTEGER PRIMARY KEY AUTOINCREMENT, parent numeric, child numeric, depth numeric);")
        self.db_cursor.execute("insert into files values(1, 'root', 0, 0, 0);")
        self.db_cursor.execute("insert into files_connect values(1, 1, 1, 0);")
        
    def __scan(self):
        """scan content of the given path"""
        # TODO: zmienić sposób pobierania danych do bazy, bo wooolne to jak pies!
        self.busy = True
        
        # jako, że to jest w osobnym wątku, a sqlite się przypieprza, że musi mieć
        # konekszyn dla tego samego wątku, więc robimy osobne połączenie dla tego zadania.
        
        db_connection = sqlite.connect("%s" % self.internal_filename,
                                       detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES,
                                       isolation_level="IMMEDIATE")
        db_cursor = db_connection.cursor()
        
        timestamp = datetime.datetime.now()
        
        mime = mimetypes.MimeTypes()
        mov_ext = ('mkv','avi','ogg','mpg','wmv','mp4','mpeg')
        img_ext = ('jpg','jpeg','png','gif','bmp','tga','tif','tiff','ilbm','iff','pcx')
        
        # count files in directory tree
        count = 0
        #if self.sbid != 0:
        #    self.status.remove(self.sbSearchCId, self.sbid)
        self.statusmsg = "Calculating number of files in directory tree..."
        
        for root,kat,plik in os.walk(self.path):
            for p in plik:
                count+=1
        if count > 0:
            step = 1.0/count
        else:
            step = 1.0
        self.count = 0
        
        def __recurse(path,name,wobj,date=0,frac=0,size=0,idWhere=1):
            """recursive scans the path
            path = path string
            name = field name
            wobj = obiekt katalogu
            date = data pliku
            frac - kolejny krok potrzebny w np. statusbarze.
            idWhere - simple id parent, or "place" where to add node
            """
            #{{{
            if self.abort:
                return -1
            _size = size
            walker = os.walk(path)
            root,dirs,files = walker.next()
            ftype = 1
            db_cursor.execute("insert into files(filename, date, size, type) values(?,?,?,?)",(name, date, 0, ftype))
            db_cursor.execute("select seq FROM sqlite_sequence WHERE name='files'")
            currentid=db_cursor.fetchone()[0]
            db_cursor.execute("insert into files_connect(parent,child,depth) values(?,?,?)",(currentid, currentid, 0))
            
            if idWhere>0:
                db_cursor.execute("insert into files_connect(parent, child, depth) select r1.parent, r2.child, r1.depth + r2.depth + 1 as depth FROM files_connect r1, files_connect r2 WHERE r1.child = ? AND r2.parent = ? ",(idWhere, currentid))
            
            for i in dirs:
                st = os.stat(os.path.join(root,i))
                dirsize = __recurse(os.path.join(path,i),i,wobj,st.st_mtime,frac,0,currentid)
                if dirsize == -1:
                    break
                else:
                    _size = _size + dirsize
            
            for i in files:
                if self.abort:
                    break
                self.count = self.count + 1
                st = os.stat(os.path.join(root,i))
                
                ### scan files
                # if i[-3:].lower() in mov_ext or \
                # mime.guess_type(i)!= (None,None) and \
                # mime.guess_type(i)[0].split("/")[0] == 'video':
                    # # video only
                    # info = filetypeHelper.guess_video(os.path.join(root,i))
                # elif i[-3:].lower() in img_ext or \
                # mime.guess_type(i)!= (None,None) and \
                # mime.guess_type(i)[0].split("/")[0] == 'image':
                    # pass
                ### end of scan
                
                ### progress/status
                # if wobj.sbid != 0:
                    # wobj.status.remove(wobj.sbSearchCId, wobj.sbid)
                self.statusmsg = "Scannig: %s" % (os.path.join(root,i))
                self.progress = frac * self.count
                # # PyGTK FAQ entry 23.20
                # while gtk.events_pending(): gtk.main_iteration()
                
                _size = _size + st.st_size
                
                db_cursor.execute('insert into files(filename, date, size, type) values(?,?,?,?)',(i, st.st_mtime, st.st_size,2))
                db_cursor.execute("select seq FROM sqlite_sequence WHERE name='files'")
                currentfileid=db_cursor.fetchone()[0]
                db_cursor.execute("insert into files_connect(parent,child,depth) values(?,?,?)",(currentfileid, currentfileid, 0))
                if currentid>0:
                    db_cursor.execute("insert into files_connect(parent, child, depth) select r1.parent, r2.child, r1.depth + r2.depth + 1 as depth FROM files_connect r1, files_connect r2 WHERE r1.child = ? AND r2.parent = ? ",(currentid, currentfileid))
            
            db_cursor.execute("update files set size=? where id=?",(_size, currentid))
            if self.abort:
                return -1
            else:
                return _size
            #}}}
        
        if __recurse(self.path,self.label,self,0,step) == -1:
            db_cursor.close()
            db_connection.rollback()
        else:
            db_cursor.close()
            db_connection.commit()
            self.__prepare_discs_treemodel()
        db_connection.close()
        
        if __debug__:
            print "scan time: ", (datetime.datetime.now() - timestamp)
        
        self.modified = True
        self.busy = False
        #self.__display_main_tree()
        
        self.statusmsg = "Idle"
        self.progress = 0
        self.abort = False
            
    def __prepare_discs_treemodel(self):
        """load data from DB to tree model"""
        
        # cleanup treeStore
        self.discsTree.clear()
        
        #connect
        db_connection = sqlite.connect("%s" % self.internal_filename,
                                       detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        db_cursor = db_connection.cursor()
        db_cursor.execute("select count(id) from files where type=1")
        count = db_cursor.fetchone()[0]
        if count>0:
            step = 1.0/self.count
        else:
            step = 1.0
        count = 0
        
        self.statusmsg = "Fetching data from catalog file"
            
        def get_children(id, name, parent):
            """fetch all children and place them in model"""
            #{{{
            myiter = self.discsTree.insert_before(parent,None)
            self.discsTree.set_value(myiter,0,id)
            self.discsTree.set_value(myiter,1,name)
            
            # isroot?
            if parent == None:
                self.discsTree.set_value(myiter,2,gtk.STOCK_CDROM)
            else:
                self.discsTree.set_value(myiter,2,gtk.STOCK_DIRECTORY)
            db_cursor.execute("SELECT o.child, f.filename FROM files_connect o LEFT JOIN files f ON o.child=f.id WHERE o.parent=? AND o.depth=1 AND f.type=1 ORDER BY f.filename",(id,))
            
            # progress
            self.progress = step * self.count
            
            for cid,name in db_cursor.fetchall():
                get_children(cid, name, myiter)
            #}}}
            
        # get initial roots from first, default root (id: 1) in the tree,
        # and then add other subroots to tree model
        if __debug__:
            data = datetime.datetime.now()
        db_cursor.execute("SELECT o.child, f.filename FROM files_connect o LEFT JOIN files f ON o.child=f.id WHERE o.parent=1 AND o.depth=1 AND f.type=1 ORDER BY f.filename")
        
        # real volumes:
        for id,name in db_cursor.fetchall():
            get_children(id,name,None)
        if __debug__:
            print "tree generation time: ", (datetime.datetime.now() - data)
        
        self.statusmsg = "Idle"
        self.progress = 0
        
        return
        
    pass # end of class
