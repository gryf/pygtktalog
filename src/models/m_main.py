# This Python file uses the following encoding: utf-8
#
#  Author: Roman 'gryf' Dobosz  gryf@elysium.pl
#
#  Copyright (C) 2007 by Roman 'gryf' Dobosz
#
#  This file is part of pyGTKtalog.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

#  -------------------------------------------------------------------------

import os
import sys
import base64
import shutil
import tarfile

import gtk
import gobject

from gtkmvc.model_mt import ModelMT

from pysqlite2 import dbapi2 as sqlite
from datetime import datetime
#import mx.DateTime
try:
    import threading as _threading
except ImportError:
    if __debug__:
        print "m_main.py: import exception: _threading"
    import dummy_threading as _threading
try:
    import Image, ImageEnhance
except:
    if __debug__:
        print "m_main.py: import exception: Image|ImageEnhance"
    pass

from utils import EXIF

from m_config import ConfigModel
from m_details import DetailsModel

class Thumbnail(object):
    def __init__(self, *args):
        self.x = None
        self.y = None
    
class Picture(object):
    def __init__(self, *args):
        self.x = None
        self.y = None

class MainModel(ModelMT):
    """Create, load, save, manipulate db file which is container for data"""
    
    __properties__ = {'busy': False, 'statusmsg': '', 'progress': 0}
    
    # constants instead of dictionary tables
    # type of files
    LAB = 0 # root of the tree - label/collection name
    DIR = 1 # directory
    FIL = 2 # file
    LIN = 3 # symbolic link
    
    # filetype kind of
    F_UNK = 0 # unknown - default
    F_IMG = 1 # images - jpg, gif, tiff itd
    F_MOV = 2 # movies and clips - mpg, ogm, mkv, avi, asf, wmv itd
    F_MUS = 4 # music - flac, mp3, mpc, ogg itd
    F_APP = 5 # applications
    F_DOC = 6 # all kind of documents txt/pdf/doc/odf itd
    
    CD = 1 # sorce: cd/dvd
    DR = 2 # source: filesystem
    
    def __init__(self):
        ModelMT.__init__(self)
        self.config = ConfigModel()
        self.unsaved_project = False
        self.filename = None # collection saved/opened filename
        self.internal_dirname = None
        self.db_connection = None
        self.db_cursor = None
        self.abort = False
        self.source = self.CD
        self.config.load()
        self.details = DetailsModel()
        
        # Directory tree: id, nazwa, ikonka, typ
        self.discs_tree = gtk.TreeStore(gobject.TYPE_INT, gobject.TYPE_STRING,
                                        str, gobject.TYPE_INT)
        # File list of selected directory: child_id(?), filename, size,
        # date, type, icon
        self.files_list = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING,
                                        gobject.TYPE_UINT64,
                                        gobject.TYPE_STRING, gobject.TYPE_INT,
                                        gobject.TYPE_STRING, str)
        # Tag list: id, name, count
        self.tags_list = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING,
                                       gobject.TYPE_UINT64, str)
        
        return
        
    def cleanup(self):
        self.__close_db_connection()
        if self.internal_dirname != None:
            try:
                shutil.rmtree(self.internal_dirname)
            except:
                if __debug__:
                    print "m_main.py: cleanup()", self.internal_dirname
                pass
        return
        
    def load(self):
        pass
        
    def new(self):
        self.unsaved_project = False
        self.__create_internal_dirname()
        self.__connect_to_db()
        self.__create_database()
        
        self.__clear_trees()
        
        return
        
    def save(self, filename=None):
        if filename:
            self.filename = filename
        self.__compress_and_save()
        return
        
    def open(self, filename=None):
        """try to open db file"""
        self.unsaved_project = False
        self.__create_internal_dirname()
        self.filename = filename
        
        try:
            tar = tarfile.open(filename, "r:gz")
        except:
            try:
                tar = tarfile.open(filename, "r")
            except:
                print "%s: file cannot be read!" % filename
                self.filename = None
                self.internal_dirname = None
                return
                
        os.chdir(self.internal_dirname)
        tar.extractall()
        tar.close()
        
        self.__connect_to_db()
        self.__fetch_db_into_treestore()
        self.config.add_recent(filename)
        
        return True
            
    def scan(self, path, label):
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
        
    def get_root_entries(self, id=None):
        """Get all children down from sepcified root"""
        try:
            self.files_list.clear()
        except:
            pass
        # parent for virtual '..' dir
        #myiter = self.filemodel.insert_before(None,None)
        #self.cur.execute("SELECT parent FROM files_connect WHERE child=? AND depth = 1",(id,))
        #self.filemodel.set_value(myiter,0,self.cur.fetchone()[0])
        #self.filemodel.set_value(myiter,1,'..')
        #if __debug__:
        #    print datetime.fromtimestamp(ch[3])
        
        # directories first
        self.db_cursor.execute("SELECT id, filename, size, date FROM files \
                               WHERE parent_id=? AND type=1 \
                               ORDER BY filename", (id,))
        data = self.db_cursor.fetchall()
        for ch in data:
            myiter = self.files_list.insert_before(None, None)
            self.files_list.set_value(myiter, 0, ch[0])
            self.files_list.set_value(myiter, 1, ch[1])
            self.files_list.set_value(myiter, 2, ch[2])
            self.files_list.set_value(myiter, 3,
                                      datetime.fromtimestamp(ch[3]))
            self.files_list.set_value(myiter, 4, 1)
            self.files_list.set_value(myiter, 5, 'direktorja')
            self.files_list.set_value(myiter, 6, gtk.STOCK_DIRECTORY)
            
        # all the rest
        self.db_cursor.execute("SELECT id, filename, size, date, type \
                               FROM files WHERE parent_id=? AND type!=1 \
                               ORDER BY filename", (id,))
        data = self.db_cursor.fetchall()
        for ch in data:
            myiter = self.files_list.insert_before(None, None)
            self.files_list.set_value(myiter, 0, ch[0])
            self.files_list.set_value(myiter, 1, ch[1])
            self.files_list.set_value(myiter, 2, ch[2])
            self.files_list.set_value(myiter, 3, datetime.fromtimestamp(ch[3]))
            self.files_list.set_value(myiter, 4, ch[4])
            self.files_list.set_value(myiter, 5, 'kategoria srategoria')
            if ch[4] == self.FIL:
                self.files_list.set_value(myiter, 6, gtk.STOCK_FILE)
            elif ch[4] == self.LIN:
                self.files_list.set_value(myiter, 6, gtk.STOCK_INDEX)
        return
        
    def get_file_info(self, id):
        """get file info from database"""
        self.db_cursor.execute("SELECT filename, date, size, type \
                               FROM files WHERE id = ?", (id,))
        set = self.db_cursor.fetchone()
        if set == None:
            return ''
            
        string = "Filename: %s\nDate: %s\nSize: %s\ntype: %s" % \
            (set[0], datetime.fromtimestamp(set[1]), set[2], set[3])
        return string
        
    def get_source(self, path):
        """get source of top level directory"""
        bid = self.discs_tree.get_value(self.discs_tree.get_iter(path[0]),
                                        0)
        self.db_cursor.execute("select source from files where id = ?",
                               (bid,))
        res = self.db_cursor.fetchone()
        if res == None:
            return False
        return int(res[0])
        
    def get_label_and_filepath(self, path):
        """get source of top level directory"""
        bid = self.discs_tree.get_value(self.discs_tree.get_iter(path[0]),
                                        0)
        self.db_cursor.execute("select filepath, filename from files \
                               where id = ? and parent_id = 1", (bid,))
        res = self.db_cursor.fetchone()
        if res == None:
            return None, None
        return res[0], res[1]
        
    def delete(self, branch_iter):
        if not branch_iter:
            return
        self.__remove_branch_form_db(self.discs_tree.get_value(branch_iter,0))
        self.discs_tree.remove(branch_iter)
        return
        
    # private class functions
    def __clear_trees(self):
        self.__clear_tags_tree()
        self.__clear_files_tree()
        self.__clear_discs_tree()
        
    def __clear_tags_tree(self):
        try:
            self.tags_list.clear()
        except:
            pass
    
    def __clear_discs_tree(self):
        try:
            self.discs_tree.clear()
        except:
            pass
            
    def __clear_files_tree(self):
        try:
            self.files_list.clear()
        except:
            pass
            
    def __connect_to_db(self):
        self.db_connection = sqlite.connect("%s" % \
                    (self.internal_dirname + '/db.sqlite'),
                    detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
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
        
    def __create_internal_dirname(self):
        self.cleanup()
        self.internal_dirname = "/tmp/pygtktalog%d" % datetime.now().microsecond
        try:
            os.mkdir(self.internal_dirname)
        except:
            if __debug__:
                print "m_main.py: __create_internal_dirname(): cannot create \
                temporary directory, or directory exists"
            pass
        return
    
    def __compress_and_save(self):
        if self.config.confd['compress']:
            tar = tarfile.open(self.filename, "w:gz")
        else:
            tar = tarfile.open(self.filename, "w")
        
        os.chdir(self.internal_dirname)
        tar.add('.')
        tar.close()
            
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
                                     source integer,
                                     size_x integer,
                                     size_y integer,
                                     filetype integer,
                                     note TEXT);""")
        self.db_cursor.execute("""create table 
                               tags(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    file_id INTEGER,
                                    tag TEXT);""")
        self.db_cursor.execute("""create table 
                               descriptions(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            file_id INTEGER,
                                            desc TEXT,
                                            image TEXT,
                                            image_x INTEGER,
                                            image_y INTEGER,
                                            thumb TEXT,
                                            thumb_x INTEGER,
                                            thumb_y INTEGER,
                                            thumb_mode TEXT);""")
        self.db_cursor.execute("insert into files values(1, 1, 'root', null, \
                               0, 0, 0, 0, null, null, null, null);")
        
    def __scan(self):
        """scan content of the given path"""
        self.busy = True
        
        # new conection for this task, because it's running in separate thread
        db_connection = sqlite.connect("%s" % \
                   (self.internal_dirname + '/db.sqlite'),
                   detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES,
                   isolation_level="EXCLUSIVE")
        db_cursor = db_connection.cursor()
        
        timestamp = datetime.now()
        
        # TODO: file types has to be moved to configuration model
        mov_ext = ('mkv', 'avi', 'ogg', 'mpg', 'wmv', 'mp4', 'mpeg')
        img_ext = ('jpg','jpeg','png','gif','bmp','tga','tif','tiff','ilbm','iff','pcx')
        
        # count files in directory tree
        count = 0
        self.statusmsg = "Calculating number of files in directory tree..."
        
        count = 0
        try:
            for root, dirs, files in os.walk(self.path):
                count += len(files)
        except:
            if __debug__:
                print 'm_main.py: os.walk in %s' % self.path
            pass
        
        if count > 0:
            step = 1.0/count
        else:
            step = 1.0
        self.count = 0
        
        # guess filesystem encoding
        self.fsenc = sys.getfilesystemencoding()
        
        self.fresh_disk_iter = None
        
        def __recurse(parent_id, name, path, date, size, filetype,
                      discs_tree_iter=None):
            """recursive scans given path"""
            if self.abort:
                return -1
            
            _size = size
            
            myit = self.discs_tree.append(discs_tree_iter,None)
            
            if parent_id == 1:
                self.fresh_disk_iter = myit
                self.discs_tree.set_value(myit,2,gtk.STOCK_CDROM)
                sql = """insert into 
                    files(parent_id, filename, filepath, date, size, type, source)
                    values(?,?,?,?,?,?,?)"""
                db_cursor.execute(sql, (parent_id, name, path, date, size,
                                        filetype, self.source))
            else:
                self.discs_tree.set_value(myit,2,gtk.STOCK_DIRECTORY)
                sql = """
                insert into
                files(parent_id, filename, filepath, date, size, type)
                values(?,?,?,?,?,?)
                """
                db_cursor.execute(sql,
                                  (parent_id, name, path, date, size, filetype))
                
            sql = """select seq FROM sqlite_sequence WHERE name='files'"""
            db_cursor.execute(sql)
            currentid=db_cursor.fetchone()[0]
            
            self.discs_tree.set_value(myit,0,currentid)
            self.discs_tree.set_value(myit,1,name)
            self.discs_tree.set_value(myit,3,parent_id)
            
            try:
                root,dirs,files = os.walk(path).next()
            except:
                if __debug__:
                    print "m_main.py: cannot access ", path
                #return -1
                return 0
                
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
                    
                # do NOT follow symbolic links
                if os.path.islink(os.path.join(root,i)):
                    l = os.readlink(os.path.join(root,i))
                    if self.fsenc:
                        l = l.decode(self.fsenc)
                    else:
                        l = l
                        
                    sql = """
                    insert into files(parent_id, filename, filepath, date, size, type)
                    values(?,?,?,?,?,?)
                    """
                    db_cursor.execute(sql, (currentid, j + " -> " + l,
                                            os.path.join(path,i), st_mtime, 0,
                                            self.LIN))
                    dirsize = 0
                else:
                    dirsize = __recurse(currentid, j, os.path.join(path,i),
                                        st_mtime, 0, self.DIR, myit)
                
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
                    
                ### TODO: scan files
                #if i.split('.').[-1].lower() in mov_ext:
                    # # video only
                    # info = filetypeHelper.guess_video(os.path.join(root,i))
                    
                
                if i.split('.')[-1].lower() in img_ext:
                    exif_info = EXIF.process_file(open(os.path.join(path,i),
                                                       'rb'))
                    if exif_info.has_key('JPEGThumbnail'):
                        print "%s got thumbnail" % i
                    else:
                        print "%s has not got thumbnail" % i
                    
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
                    
                sql = """
                insert into files(parent_id, filename, filepath, date, size, type)
                values(?,?,?,?,?,?)
                """
                db_cursor.execute(sql, (currentid, j, os.path.join(path,i),
                                        st_mtime, st_size, self.FIL))
            
            sql = """update files set size=? where id=?"""
            db_cursor.execute(sql,(_size, currentid))
            if self.abort:
                return -1
            else:
                return _size
        
        if __recurse(1, self.label, self.path, 0, 0, self.DIR) == -1:
            if __debug__:
                print "m_main.py: __scan() __recurse() \
                interrupted self.abort = True"
            self.discs_tree.remove(self.fresh_disk_iter)
            db_cursor.close()
            db_connection.rollback()
        else:
            if __debug__:
                print "m_main.py: __scan() __recurse() goes without interrupt"
            db_cursor.close()
            db_connection.commit()
        db_connection.close()
        if __debug__:
            print "m_main.py: __scan() time: ", (datetime.now() - timestamp)
        
        self.busy = False
        
        self.statusmsg = "Idle"
        self.progress = 0
        self.abort = False
            
    def __fetch_db_into_treestore(self):
        """load data from DB to tree model"""
        # cleanup treeStore
        self.__clear_discs_tree()
        
        #connect
        db_connection = sqlite.connect("%s" % \
                                       (self.internal_dirname + '/db.sqlite'),
                                       detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        db_cursor = db_connection.cursor()
        
        # fetch all the directories
        try:
            sql = """
            SELECT id, parent_id, filename FROM files 
            WHERE type=1 ORDER BY parent_id, filename
            """
            db_cursor.execute(sql)
            data = db_cursor.fetchall()
        except:
            # cleanup
            self.cleanup()
            self.filename = None
            self.internal_dirname = None
            print "%s: Wrong database format!" % self.filename
            return
        
        def get_children(parent_id = 1, iterator = None):
            """fetch all children and place them in model"""
            for row in data:
                if row[1] == parent_id:
                    myiter = self.discs_tree.insert_before(iterator, None)
                    self.discs_tree.set_value(myiter, 0, row[0]) # id
                    self.discs_tree.set_value(myiter, 1, row[2]) # name
                    self.discs_tree.set_value(myiter, 3, row[1]) # parent_id
                    get_children(row[0], myiter)
                    
                    # isroot?
                    if iterator == None:
                        self.discs_tree.set_value(myiter, 2, gtk.STOCK_CDROM)
                    else:
                        self.discs_tree.set_value(myiter, 2,
                                                  gtk.STOCK_DIRECTORY)
            return
           
        if __debug__:
            start_date = datetime.now()
        # launch scanning.
        get_children()
        if __debug__:
            print "m_main.py: __fetch_db_into_treestore() tree generation time: ",
            (datetime.now() - start_date)
        db_connection.close()
        return
        
    def __remove_branch_form_db(self, root_id):
        parent_ids = [root_id,]
        sql = """select id from files where parent_id = ? and type = 1"""
        self.db_cursor.execute(sql, (root_id,))
        ids = self.db_cursor.fetchall()
        
        def get_children(fid):
            parent_ids.append(fid)
            sql = """select id from files where parent_id = ? and type = 1"""
            self.db_cursor.execute(sql, (fid,))
            res = self.db_cursor.fetchall()
            for i in res:
                get_children(i[0])
                
        for i in ids:
            get_children(i[0])
        
        def generator():
            for c in parent_ids:
                yield (c,)
            
        sql = """delete from files where type = 1 and parent_id = ?"""
        self.db_cursor.executemany(sql, generator())
        sql = """delete from files where id = ?"""
        self.db_cursor.executemany(sql, generator())
        self.db_connection.commit()
        return
        
             
    def __append_added_volume(self):
        """append branch from DB to existing tree model"""
        #connect
        db_connection = sqlite.connect("%s" % \
                                       (self.internal_dirname + '/db.sqlite'),
                                       detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        db_cursor = db_connection.cursor()
        
        sql = """SELECT id, parent_id, filename FROM files WHERE type=1 ORDER BY parent_id, filename"""
        db_cursor.execute(sql)
        data = db_cursor.fetchall()
        
        def get_children(parent_id = 1, iterator = None):
            """fetch all children and place them in model"""
            for row in data:
                if row[1] == parent_id:
                    myiter = self.discs_tree.insert_before(iterator, None)
                    self.discs_tree.set_value(myiter, 0, row[0])
                    self.discs_tree.set_value(myiter, 1, row[2])
                    self.discs_tree.set_value(myiter, 3, row[1])
                    get_children(row[0], myiter)
                    
                    # isroot?
                    if iterator == None:
                        self.discs_tree.set_value(myiter, 2, gtk.STOCK_CDROM)
                    else:
                        self.discs_tree.set_value(myiter, 2,
                                                  gtk.STOCK_DIRECTORY)
            return
           
        if __debug__:
            start_date = datetime.now()
        # launch scanning.
        get_children()
        if __debug__:
            print "m_main.py: __fetch_db_into_treestore() tree generation time: ",
            (datetime.now() - start_date)
        db_connection.close()
        return
        
    pass # end of class
