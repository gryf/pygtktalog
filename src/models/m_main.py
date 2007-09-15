# This Python file uses the following encoding: utf-8

import utils._importer
import utils.globals
from gtkmvc.model_mt import ModelMT

try:
    import threading as _threading
except ImportError:
    if __debug__:
        print "m_main.py: import exception: _threading"
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
    
    
    # Drzewo katalogów: id, nazwa, ikonka, typ
    discsTree = gtk.TreeStore(gobject.TYPE_INT, gobject.TYPE_STRING, str, gobject.TYPE_INT)
    # Lista plików wskazanego katalogu: child_id (?), filename, size, date, typ, ikonka
    filesList = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_UINT64, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, str)
    
    LAB = 0 # label/nazwa kolekcji --- najwyższy poziom drzewa przypiętego do korzenia
    DIR = 1 # katalog - podlega innemu katalogu lub lejbelu
    FIL = 2 # plik - podleka katalogu lub lejbelu
    
    CD = 1 # podczas skanowania, wstawiane jest źródło na płytę CD/DVD
    DR = 2 # podczas skanowania, wstawiane jest źródło na katalog w fs
    
    # default source is CD/DVD
    source = CD
    
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
                    print "m_main.py: cleanup()", self.internal_filename
                pass
            try:
                os.unlink(self.internal_filename + '-journal')
            except:
                if __debug__:
                    print "m_main.py: cleanup()", self.internal_filename+'-journal'
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
        
        try:
            source = bz2.BZ2File(filename, 'rb')
        except:
            print "%s: file cannot be read!" % self.filename
            self.filename = None
            self.internal_filename = None
            return
        
        destination = open(self.internal_filename, 'wb')
        while True:
            try:
                data = source.read(1024000)
            except:
                # smth went wrong
                print "%s: Wrong database format!" % self.filename
                if __debug__:
                    print "m_main.py: open() something goes bad"
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
        self.config.add_recent(filename)
        
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
        self.db_cursor.execute("SELECT id, filename, size, date FROM files WHERE parent_id=? AND type=1 ORDER BY filename",(id,))
        data = self.db_cursor.fetchall()
        for ch in data:
            myiter = self.filesList.insert_before(None,None)
            self.filesList.set_value(myiter,0,ch[0])
            self.filesList.set_value(myiter,1,ch[1])
            self.filesList.set_value(myiter,2,ch[2])
            self.filesList.set_value(myiter,3,datetime.datetime.fromtimestamp(ch[3]))
            self.filesList.set_value(myiter,4,1)
            self.filesList.set_value(myiter,5,'direktorja')
            self.filesList.set_value(myiter,6,gtk.STOCK_DIRECTORY)
            
        # all the rest
        self.db_cursor.execute("SELECT id, filename, size, date, type FROM files WHERE parent_id=? AND type!=1 ORDER BY filename",(id,))
        data = self.db_cursor.fetchall()
        for ch in data:
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
        
    def get_file_info(self, id):
        """get file info from database"""
        self.db_cursor.execute("SELECT filename, date, size, type FROM files WHERE id = ?",(id,))
        set = self.db_cursor.fetchone()
        if set == None:
            return ''
            
        string = "Filename: %s\nDate: %s\nSize: %s\ntype: %s" % (set[0],datetime.datetime.fromtimestamp(set[1]),set[2],set[3])
        return string
        
    def get_source(self, path):
        """get source of top level directory"""
        bid = self.discsTree.get_value(self.discsTree.get_iter(path[0]),0)
        self.db_cursor.execute("select source from files where id = ?", (bid,))
        res = self.db_cursor.fetchone()
        if res == None:
            return False
        return int(res[0])
        
    def get_label_and_filepath(self, path):
        """get source of top level directory"""
        bid = self.discsTree.get_value(self.discsTree.get_iter(path[0]),0)
        self.db_cursor.execute("select filepath, filename from files where id = ? and parent_id = 1", (bid,))
        res = self.db_cursor.fetchone()
        if res == None:
            return None, None
        return res[0], res[1]
        
    def delete(self, branch_iter):
        if not branch_iter:
            return
        self.__remove_branch_form_db(self.discsTree.get_value(branch_iter,0))
        self.discsTree.remove(branch_iter)
        return
        
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
        self.db_cursor.execute("""create table 
                               files(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     parent_id INTEGER,
                                     filename TEXT,
                                     filepath TEXT,
                                     date datetime,
                                     size integer,
                                     type integer,
                                     source integer);""")
        self.db_cursor.execute("insert into files values(1, 1, 'root', null, 0, 0, 0, 0);")
        
    def __scan(self):
        """scan content of the given path"""
        self.busy = True
        
        # jako, że to jest w osobnym wątku, a sqlite się przypieprza, że musi mieć
        # konekszyn dla tego samego wątku, więc robimy osobne połączenie dla tego zadania.
        db_connection = sqlite.connect("%s" % self.internal_filename,
                                       detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES,
                                       isolation_level="EXCLUSIVE")
        db_cursor = db_connection.cursor()
        
        timestamp = datetime.datetime.now()
        
        mime = mimetypes.MimeTypes()
        mov_ext = ('mkv','avi','ogg','mpg','wmv','mp4','mpeg')
        img_ext = ('jpg','jpeg','png','gif','bmp','tga','tif','tiff','ilbm','iff','pcx')
        
        # count files in directory tree
        count = 0
        self.statusmsg = "Calculating number of files in directory tree..."
        
        count = 0
        for root, dirs, files in os.walk(self.path):
            count += len(files)
        
        if count > 0:
            step = 1.0/count
        else:
            step = 1.0
        self.count = 0
        
        # guess filesystem encoding
        self.fsenc = sys.getfilesystemencoding()
        
        self.fresh_disk_iter = None
        
        def __recurse(parent_id, name, path, date, size, filetype, discs_tree_iter=None):
            """recursive scans the path"""
            if self.abort:
                return -1
            
            _size = size
            
            myit = self.discsTree.append(discs_tree_iter,None)
            
            if parent_id == 1:
                self.fresh_disk_iter = myit
                self.discsTree.set_value(myit,2,gtk.STOCK_CDROM)
                db_cursor.execute("insert into files(parent_id, filename, filepath, date, size, type, source) values(?,?,?,?,?,?,?)",
                                  (parent_id, name, path, date, size, filetype, self.source))
            else:
                self.discsTree.set_value(myit,2,gtk.STOCK_DIRECTORY)
                db_cursor.execute("insert into files(parent_id, filename, filepath, date, size, type) values(?,?,?,?,?,?)",
                                  (parent_id, name, path, date, size, filetype))
            db_cursor.execute("select seq FROM sqlite_sequence WHERE name='files'")
            currentid=db_cursor.fetchone()[0]
            
            self.discsTree.set_value(myit,0,currentid)
            self.discsTree.set_value(myit,1,name)
            self.discsTree.set_value(myit,3,parent_id)
            
            root,dirs,files = os.walk(path).next()
            
            for i in dirs:
                if self.fsenc:
                    j = i.decode(self.fsenc)
                else:
                    j = i
                try:
                    st = os.stat(os.path.join(root,i))
                    st_mtime = st.st_mtime
                except OSError:
                    st_mtime = 0
                    
                dirsize = __recurse(currentid, j, os.path.join(path,i), st_mtime, 0, self.DIR, myit)
                
                if dirsize == -1:
                    break
                else:
                    _size = _size + dirsize
            
            for i in files:
                if self.abort:
                    break
                self.count = self.count + 1
                try:
                    st = os.stat(os.path.join(root,i))
                    st_mtime = st.st_mtime
                    st_size = st.st_size
                except OSError:
                    st_mtime = 0
                    st_size = 0
                    
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
                    self.progress = step * self.count
                # # PyGTK FAQ entry 23.20
                # while gtk.events_pending(): gtk.main_iteration()
                
                _size = _size + st_size
                j = i
                if self.fsenc:
                    j = i.decode(self.fsenc)
                db_cursor.execute("insert into files(parent_id, filename, filepath, date, size, type) values(?,?,?,?,?,?)",
                                  (currentid, j, os.path.join(path,i), st_mtime, st_size, self.FIL))
            
            db_cursor.execute("update files set size=? where id=?",(_size, currentid))
            if self.abort:
                return -1
            else:
                return _size
        
        
        if __recurse(1, self.label, self.path, 0, 0, self.DIR) == -1:
            if __debug__:
                print "m_main.py: __scan() __recurse() interrupted self.abort = True"
            self.discsTree.remove(self.fresh_disk_iter)
            db_cursor.close()
            db_connection.rollback()
        else:
            if __debug__:
                print "m_main.py: __scan() __recurse() goes without interrupt"
            db_cursor.close()
            db_connection.commit()
        db_connection.close()
        if __debug__:
            print "m_main.py: __scan() time: ", (datetime.datetime.now() - timestamp)
        
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
        try:
            db_cursor.execute("SELECT id, parent_id, filename FROM files WHERE type=1 ORDER BY parent_id, filename")
            data = db_cursor.fetchall()
        except:
            # cleanup
            self.cleanup()
            self.filename = None
            self.internal_filename = None
            print "%s: Wrong database format!" % self.filename
            return
        
        def get_children(parent_id = 1, iterator = None):
            """fetch all children and place them in model"""
            for row in data:
                if row[1] == parent_id:
                    myiter = self.discsTree.insert_before(iterator,None)
                    self.discsTree.set_value(myiter,0,row[0]) # id
                    self.discsTree.set_value(myiter,1,row[2]) # name
                    self.discsTree.set_value(myiter,3,row[1]) # parent_id
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
            print "m_main.py: __fetch_db_into_treestore() tree generation time: ", (datetime.datetime.now() - start_date)
        db_connection.close()
        return
        
    def __remove_branch_form_db(self, root_id):
        parent_ids = [root_id,]
        self.db_cursor.execute("select id from files where parent_id = ? and type = 1", (root_id,))
        ids = self.db_cursor.fetchall()
        
        def get_children(fid):
            parent_ids.append(fid)
            self.db_cursor.execute("select id from files where parent_id = ? and type = 1", (fid,))
            res = self.db_cursor.fetchall()
            for i in res:
                get_children(i[0])
                
        for i in ids:
            get_children(i[0])
        
        def generator():
            for c in parent_ids:
                yield (c,)
            
        self.db_cursor.executemany("delete from files where type = 1 and parent_id = ?", generator())
        self.db_cursor.executemany("delete from files where id = ?",generator())
        self.db_connection.commit()
        return
        
             
    def __append_added_volume(self):
        """append branch from DB to existing tree model"""
        #connect
        db_connection = sqlite.connect("%s" % self.internal_filename,
                                       detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        db_cursor = db_connection.cursor()
        
        db_cursor.execute("SELECT id, parent_id, filename FROM files WHERE type=1 ORDER BY parent_id, filename")
        data = db_cursor.fetchall()
        
        def get_children(parent_id = 1, iterator = None):
            """fetch all children and place them in model"""
            for row in data:
                if row[1] == parent_id:
                    myiter = self.discsTree.insert_before(iterator,None)
                    self.discsTree.set_value(myiter,0,row[0])
                    self.discsTree.set_value(myiter,1,row[2])
                    self.discsTree.set_value(myiter,3,row[1])
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
            print "m_main.py: __fetch_db_into_treestore() tree generation time: ", (datetime.datetime.now() - start_date)
        db_connection.close()
        return
        
    pass # end of class
