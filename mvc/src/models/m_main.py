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
import sys
import mimetypes
import bz2

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
    db_connection = None
    db_cursor = None
    abort = False
    discsTree = gtk.TreeStore(gobject.TYPE_INT, gobject.TYPE_STRING,str)
    filesList = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_UINT64, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING,str)
    
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
                    print "cleanup()", self.internal_filename
                pass
            try:
                os.unlink(self.internal_filename + '-journal')
            except:
                if __debug__:
                    print "cleanup()", self.internal_filename+'-journal'
                pass
        return
        
    def load(self):
        pass
        
    def new(self):
        self.unsaved_project = False
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
        
    def save(self, filename=None):
        if filename:
            self.filename = filename
        self.__compress_and_save()
        return
        
    def open(self, filename=None):
        """try to open db file"""
        self.unsaved_project = False
        self.__create_internal_filename()
        self.filename = filename
        
        source = bz2.BZ2File(filename, 'rb')
        destination = open(self.internal_filename, 'wb')
        while True:
            try:
                data = source.read(1024000)
            except:
                # smth went wrong
                if __debug__:
                    print "something goes bad"
                self.filename = None
                self.internal_filename = None
                try:
                    self.discsTree.clear()
                except:
                    pass
                    
                try:
                    self.filesList.clear()
                except:
                    pass
                return False
            if not data: break
            destination.write(data)
        destination.close()
        source.close()
        
        self.__connect_to_db()
        self.__fetch_db_into_treestore()
        
        return True
            
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
            
        string = "Filename: %s\nDate: %s\nSize: %s\ntype: %s" % (set[0],datetime.datetime.fromtimestamp(set[1]),set[2],set[3])
        return string
        
    # private class functions
    def __connect_to_db(self):
        self.db_connection = sqlite.connect("%s" % self.internal_filename, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.db_cursor = self.db_connection.cursor()
        return
    
    def __close_db_connection(self):
        if self.db_cursor != None:
            self.db_cursor.close()
            self.db_cursor = None
        if self.db_connection != None:
            self.db_connection.close()
            self.db_connection = None
        return
        
    def __create_internal_filename(self):
        self.cleanup()
        self.internal_filename = "/tmp/pygtktalog%d.db" % datetime.datetime.now().microsecond
        return
    
    def __compress_and_save(self):
        source = open(self.internal_filename, 'rb')
        destination = bz2.BZ2File(self.filename, 'w')
            
        while True:
            data = source.read(1024000)
            if not data: break
            destination.write(data)
            
        destination.close()
        source.close()
        self.unsaved_project = False
        return
    
    def __create_database(self):
        """make all necessary tables in db file"""
        self.db_cursor.execute("create table files(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, date datetime, size integer, type integer);")
        self.db_cursor.execute("create table files_connect(id INTEGER PRIMARY KEY AUTOINCREMENT, parent numeric, child numeric, depth numeric);")
        self.db_cursor.execute("insert into files values(1, 'root', 0, 0, 0);")
        self.db_cursor.execute("insert into files_connect values(1, 1, 1, 0);")
        
    def __scan(self):
        """scan content of the given path"""
        # TODO: Recursive data processing is damn slow! Think about different, faster solution
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
        self.statusmsg = "Calculating number of files in directory tree..."
        
        for root,kat,plik in os.walk(self.path):
            for p in plik:
                count+=1
        if count > 0:
            step = 1.0/count
        else:
            step = 1.0
        self.count = 0
        
        # guess filesystem encoding
        self.fsenc = sys.getfilesystemencoding()
        
        def __recurse(path,name,wobj,date=0,frac=0,size=0,idWhere=1):
            """recursive scans the path
            path = path string
            name = field name
            wobj = obiekt katalogu
            date = data pliku
            frac - kolejny krok potrzebny w np. statusbarze.
            idWhere - simple id parent, or "place" where to add node
            """
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
                if self.fsenc:
                    j = i.decode(self.fsenc)
                else:
                    j = i
                st = os.stat(os.path.join(root,i))
                dirsize = __recurse(os.path.join(path,i),j,wobj,st.st_mtime,frac,0,currentid)
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
                if self.count % 32 == 0:
                    self.statusmsg = "Scannig: %s" % (os.path.join(root,i))
                    self.progress = frac * self.count
                # # PyGTK FAQ entry 23.20
                # while gtk.events_pending(): gtk.main_iteration()
                
                _size = _size + st.st_size
                j = i
                if self.fsenc:
                    j = i.decode(self.fsenc)
                db_cursor.execute('insert into files(filename, date, size, type) values(?,?,?,?)',(j, st.st_mtime, st.st_size,2))
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
        
        if __recurse(self.path,self.label,self,0,step) == -1:
            db_cursor.close()
            db_connection.rollback()
        else:
            db_cursor.close()
            db_connection.commit()
            self.__fetch_db_into_treestore()
        db_connection.close()
        
        if __debug__:
            print "scan time: ", (datetime.datetime.now() - timestamp)
        
        self.unsaved_project = True
        self.busy = False
        
        self.statusmsg = "Idle"
        self.progress = 0
        self.abort = False
            
    def __fetch_db_into_treestore(self):
        """load data from DB to tree model"""
        # cleanup treeStore
        self.discsTree.clear()
        
        #connect
        db_connection = sqlite.connect("%s" % self.internal_filename,
                                       detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        db_cursor = db_connection.cursor()
        
        # fetch all the directories
        db_cursor.execute("SELECT f.id,o.parent,o.child, f.filename FROM files_connect o LEFT JOIN files f ON o.child=f.id WHERE o.depth=1 AND f.type=1 ORDER BY o.parent,f.filename")
        data = db_cursor.fetchall()
        
        def get_children(parent_id = 1, iterator = None):
            """fetch all children and place them in model"""
            for row in data:
                if row[1] == parent_id:
                    myiter = self.discsTree.insert_before(iterator,None)
                    self.discsTree.set_value(myiter,0,row[0])
                    self.discsTree.set_value(myiter,1,row[3])
                    get_children(row[0], myiter)
                    
                    # isroot?
                    if iterator == None:
                        self.discsTree.set_value(myiter,2,gtk.STOCK_CDROM)
                    else:
                        self.discsTree.set_value(myiter,2,gtk.STOCK_DIRECTORY)
            return
           
        if __debug__:
            start_date = datetime.datetime.now()
        # launch scanning.
        get_children()
        if __debug__:
            print "tree generation time: ", (datetime.datetime.now() - start_date)
        db_connection.close()
        return
        
    pass # end of class
