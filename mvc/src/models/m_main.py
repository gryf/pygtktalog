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
        
        db_connection = sqlite.connect("%s" % self.internal_filename, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
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
        step = 1.0/count
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
                _size = _size + __recurse(os.path.join(path,i),i,wobj,st.st_mtime,frac,0,currentid)
            
            for i in files:
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
                db_connection.commit()
            
            db_cursor.execute("update files set size=? where id=?",(_size, currentid))
            return _size
            #}}}
        
        #self.db_connection.commit()
        __recurse(self.path,self.label,self,0,step)
        
        db_connection.commit()
        db_cursor.close()
        db_connection.close()
        
        self.modified = True
        self.busy = False
        #self.__display_main_tree()
        
        #if self.sbid != 0:
        #    self.status.remove(self.sbSearchCId, self.sbid)
        self.statusmsg = "Idle"
        
        self.progress = 0
        
        if __debug__:
            print "scan time: ", (datetime.datetime.now() - timestamp)
        
    pass # end of class
