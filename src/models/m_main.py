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
import tempfile
import string

import gtk
import gobject

from gtkmvc.model_mt import ModelMT

from pysqlite2 import dbapi2 as sqlite
from datetime import datetime

try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading

from m_config import ConfigModel
try:
    from utils.thumbnail import Thumbnail
    from utils.img import Img
except:
    pass
from utils.parse_exif import ParseExif
from utils.gthumb import GthumbCommentParser

class MainModel(ModelMT):
    """Create, load, save, manipulate db file which is container for data"""
    
    __properties__ = {'busy': False, 'statusmsg': '', 'progress': 0}
    
    # constants instead of dictionary tables
    # type of files
    LAB = 0 # root of the tree - label/collection name
    DIR = 1 # directory
    FIL = 2 # file
    LIN = 3 # symbolic link
    
    CD = 1 # sorce: cd/dvd
    DR = 2 # source: filesystem
    
    EXIF_DICT= {0: 'Camera',
            1: 'Date',
            2: 'Aperture',
            3: 'Exposure program',
            4: 'Exposure bias',
            5: 'ISO',
            6: 'Focal length',
            7: 'Subject distance',
            8: 'Metering mode',
            9: 'Flash',
            10: 'Light source',
            11: 'Resolution',
            12: 'Orientation'}
    
    # images extensions - only for PIL and EXIF
    IMG = ['jpg', 'jpeg', 'gif', 'png', 'tif', 'tiff', 'tga', 'pcx', 'bmp',
           'xbm', 'xpm', 'jp2', 'jpx', 'pnm']
    
    def __init__(self):
        ModelMT.__init__(self)
        self.config = ConfigModel()
        self.unsaved_project = False
        self.filename = None # catalog saved/opened filename
        self.internal_dirname = None
        self.db_connection = None
        self.db_cursor = None
        self.abort = False
        self.source = self.CD
        self.config.load()
        
        # Directory tree: id, name, icon, type
        self.discs_tree = gtk.TreeStore(gobject.TYPE_INT, gobject.TYPE_STRING,
                                        str, gobject.TYPE_INT)
        # File list of selected directory: child_id(?), filename, size,
        # date, type, icon
        self.files_list = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING,
                                        gobject.TYPE_UINT64,
                                        gobject.TYPE_STRING, gobject.TYPE_INT,
                                        gobject.TYPE_STRING, str)
        # iconview store - id, pixbuffer
        self.images_store = gtk.ListStore(gobject.TYPE_INT, gtk.gdk.Pixbuf)
        
        # exif liststore - id, exif key, exif value
        self.exif_list = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING,
                                       gobject.TYPE_STRING)
        
        # tag cloud array element is a dict with 4 keys:
        # elem = {'id': str(id), 'name': tagname, 'size': size, 'color': color}
        # where color is in one of format:
        # - named (i.e. red, blue, black and so on)
        # - #rgb
        # - #rrggbb
        self.tag_cloud = []
        '''{'id': str(1), 'name': "bezpieczeństwo", 'size': 10, 'color': '#666'},
        {'id': str(2), 'name': "bsd", 'size': 14, 'color': '#333'},
        {'id': str(3), 'name': "debian", 'size': 18, 'color': '#333'},
        {'id': str(4), 'name': "fedora", 'size': 12, 'color': '#666'},
        {'id': str(5), 'name': "firefox", 'size': 40, 'color': '#666'},
        {'id': str(6), 'name': "gnome", 'size': 26, 'color': '#333'},
        {'id': str(7), 'name': "gentoo", 'size': 30, 'color': '#000'},
        {'id': str(8), 'name': "kde", 'size': 20, 'color': '#333'},
        {'id': str(9), 'name': "kernel", 'size': 10, 'color': '#666'},
        {'id': str(10), 'name': "windows", 'size': 18, 'color': '#333'},
        ]'''
        return
        
    def add_image(self, image, id, only_thumbs=False):
        """add single image to file/directory"""
        sql = """insert into images(file_id, thumbnail, filename) 
        values(?, null, null)"""
        self.db_cursor.execute(sql, (id,))
        self.db_connection.commit()
        
        sql = """select id from images where thumbnail is null and filename is null and file_id=?"""
        self.db_cursor.execute(sql, (id,))
        res = self.db_cursor.fetchone()
        if res:
            tp, ip, rc = Img(image, self.internal_dirname).save(res[0])
            if rc != -1:
                sql = """update images set filename=?, thumbnail=? where id=?"""
                if only_thumbs:
                    img = None
                else:
                    img = ip.split(self.internal_dirname)[1][1:]
                self.db_cursor.execute(sql,
                                      (img,
                                       tp.split(self.internal_dirname)[1][1:],
                                       res[0]))
        self.db_connection.commit()
                
    def del_images(self, id):
        """removes images and their thumbnails from selected file/dir"""
        # remove images
        sql = """select filename, thumbnail from images where file_id =?"""
        self.db_cursor.execute(sql, (id,))
        res = self.db_cursor.fetchall()
        if len(res) > 0:
            for fn in res:
                if fn[0]:
                    os.unlink(os.path.join(self.internal_dirname, fn[0]))
                os.unlink(os.path.join(self.internal_dirname, fn[1]))
        
        # remove images records
        sql = """delete from images where file_id = ?"""
        self.db_cursor.execute(sql, (id,))
        self.db_connection.commit()
        
    def delete_image(self, id):
        """removes image on specified image id"""
        sql = """select filename, thumbnail from images where id=?"""
        self.db_cursor.execute(sql, (id,))
        res = self.db_cursor.fetchone()
        if res:
            if res[0]:
                os.unlink(os.path.join(self.internal_dirname, res[0]))
            os.unlink(os.path.join(self.internal_dirname, res[1]))
            
            if __debug__:
                print "m_main.py: delete_image(): removed images:"
                print res[0]
                print res[1]
        # remove images records
        sql = """delete from images where id = ?"""
        self.db_cursor.execute(sql, (id,))
        self.db_connection.commit()
                
    def add_thumbnail(self, img_fn, id):
        """generate and add thumbnail to selected file/dir"""
        if self.config.confd['thumbs']:
            self.del_thumbnail(id)
            p, e, ret_code = Thumbnail(img_fn,
                                       base=self.internal_dirname).save(id)
            if ret_code != -1:
                sql = """insert into thumbnails(file_id, filename) values (?, ?)"""
                self.db_cursor.execute(sql,
                                       (id,
                                        p.split(self.internal_dirname)[1][1:]))
                self.db_connection.commit()
                return True
        return False
                
    def del_thumbnail(self, id):
        """removes thumbnail from selected file/dir"""
        
        # remove thumbnail files
        sql = """select filename from thumbnails where file_id=?"""
        self.db_cursor.execute(sql, (id,))
        res = self.db_cursor.fetchone()
        if res:
            os.unlink(os.path.join(self.internal_dirname, res[0]))
        
        # remove thumbs records
        sql = """delete from thumbnails where file_id=?"""
        self.db_cursor.execute(sql, (id,))
        self.db_connection.commit()
        
    def cleanup(self):
        self.__close_db_connection()
        if self.internal_dirname != None:
            try:
                shutil.rmtree(self.internal_dirname)
            except:
                pass
        return
        
    def new(self):
        self.unsaved_project = False
        self.__create_internal_dirname()
        self.__connect_to_db()
        self.__create_database()
        
        self.__clear_trees()
        
        return
        
    def save(self, filename=None):
        """save tared directory at given catalog fielname"""
        if not filename and not self.filename:
            if __debug__:
                return False, "no filename detected!"
            return
        
        if filename:
            self.filename = filename
        val, err = self.__compress_and_save()
        if not val:
            self.filename = None
        return val, err
        
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
                self.filename = None
                self.internal_dirname = None
                return
                
        os.chdir(self.internal_dirname)
        try:
            tar.extractall()
            if __debug__:
                print "m_main.py: extracted tarfile into", self.internal_dirname
        except AttributeError:
            # python's 2.4 tarfile module lacks of method extractall()
            directories = []
            for tarinfo in tar:
                if tarinfo.isdir():
                    # Extract directory with a safe mode, so that
                    # all files below can be extracted as well.
                    try:
                        os.makedirs(os.path.join('.', tarinfo.name), 0777)
                    except EnvironmentError:
                        pass
                    directories.append(tarinfo)
                else:
                    tar.extract(tarinfo, '.')

            # Reverse sort directories.
            directories.sort(lambda a, b: cmp(a.name, b.name))
            directories.reverse()

            # Set correct owner, mtime and filemode on directories.
            for tarinfo in directories:
                path = os.path.join('.', tarinfo.name)
                try:
                    os.chown(tarinfo, '.')
                    os.utime(tarinfo, '.')
                    os.chmod(tarinfo, '.')
                except:
                    if __debug__:
                        print "m_main.py: open(): setting corrext owner, mtime etc"
                    pass
        tar.close()
        
        self.__connect_to_db()
        self.__fetch_db_into_treestore()
        self.config.add_recent(filename)
        
        return True
            
    def scan(self, path, label, currentid):
        """scan files in separated thread"""
        
        # flush buffer to release db lock.
        self.db_connection.commit()
        
        self.path = path
        self.label = label
        self.currentid = currentid
        
        if self.busy:
            return
        self.thread = _threading.Thread(target=self.__scan)
        self.thread.start()
        return
        
    def rename(self, id, new_name=None):
        if new_name:
            self.db_cursor.execute("update files set filename=? \
                                   where id=?", (new_name, id))
            self.db_connection.commit()
            self.__fetch_db_into_treestore()
            self.unsaved_project = True
        else:
            if __debug__:
                print "m_main.py: rename(): no label defined"
        return
        
    def refresh_discs_tree(self):
        self.__fetch_db_into_treestore()
        
    def get_root_entries(self, id=None):
        """Get all children down from sepcified root"""
        try:
            self.files_list.clear()
        except:
            pass
            
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
        self.db_cursor.execute("SELECT f.id, f.filename, f.size, f.date, \
                               f.type FROM files f \
                               WHERE f.parent_id=? AND f.type!=1 \
                               ORDER BY f.filename", (id,))
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
        
    def get_parent_discs_value(self, child_id):
        if child_id:
            self.db_cursor.execute("SELECT parent_id FROM files where id=?", (child_id,))
            set = self.db_cursor.fetchone()
            if set:
                return set[0]
        return None
    
    def get_file_info(self, id):
        """get file info from database"""
        retval = {}
        sql = """SELECT f.filename, f.date, f.size, f.type,
                        t.filename, f.description, f.note
                FROM files f
                LEFT JOIN thumbnails t ON t.file_id = f.id
                WHERE f.id = ?"""
        self.db_cursor.execute(sql, (id,))
        set = self.db_cursor.fetchone()
        if set:
            retval['debug'] = {'id': id,
            'date': datetime.fromtimestamp(set[1]),
            'size': set[2], 'type': set[3]}
            
            retval['filename'] = set[0]
            
            if set[5]:
                retval['description'] = set[5]
                
            if set[6]:
                retval['note'] = set[6]
            
            if set[4]:
                retval['thumbnail'] = os.path.join(self.internal_dirname, set[4])
                
        sql = """SELECT id, filename, thumbnail from images WHERE file_id = ?"""
        self.db_cursor.execute(sql, (id,))
        set = self.db_cursor.fetchall()
        if set:
            self.images_store = gtk.ListStore(gobject.TYPE_INT, gtk.gdk.Pixbuf)
            for idi, img, thb in set:
                im = os.path.join(self.internal_dirname,thb)
                pix = gtk.gdk.pixbuf_new_from_file(im)
                self.images_store.append([idi, pix])
            retval['images'] = True
            
        sql = """SELECT camera, date, aperture, exposure_program,
        exposure_bias, iso, focal_length, subject_distance, metering_mode,
        flash, light_source, resolution, orientation
        from exif
        WHERE file_id = ?"""
        self.db_cursor.execute(sql, (id,))
        set = self.db_cursor.fetchone()

        if set:
            self.exif_list = gtk.ListStore(gobject.TYPE_STRING,
                                           gobject.TYPE_STRING)
            for key in self.EXIF_DICT:
                myiter = self.exif_list.insert_before(None, None)
                self.exif_list.set_value(myiter, 0, self.EXIF_DICT[key])
                self.exif_list.set_value(myiter, 1, set[key])
            retval['exif'] = True
            
        # gthumb
        sql = """SELECT note, place, date from gthumb WHERE file_id = ?"""
        self.db_cursor.execute(sql, (id,))
        set = self.db_cursor.fetchone()
        
        if set:
            retval['gthumb'] = {'note': set[0], 'place': set[1], 'date': set[2]}
            
        return retval
        
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
        bid = self.discs_tree.get_value(self.discs_tree.get_iter(path),
                                        0)
        self.db_cursor.execute("select filepath, filename from files \
                               where id = ? and parent_id = 1", (bid,))
        res = self.db_cursor.fetchone()
        if res == None:
            return None, None
        return res[0], res[1]
        
    def delete(self, root_id, db_cursor=None, db_connection=None):
        """Remove subtree from main tree, remove tags from database
        remove all possible data, like thumbnails, images, gthumb info, exif
        etc"""
        
        fids = []
        
        if not db_cursor:
            db_cursor = self.db_cursor
            
        if not db_connection:
            db_connection = self.db_connection
        
        sql = """select parent_id from files where id = ?"""
        db_cursor.execute(sql, (root_id,))
        res = db_cursor.fetchone()
        parent_id = res[0]
            
        def get_children(fid):
            fids.append(fid)
            sql = """select id from files where parent_id = ?"""
            db_cursor.execute(sql, (fid,))
            res = db_cursor.fetchall()
            if len(res)>0:
                for i in res:
                    get_children(i[0])
                
        get_children(root_id)
        
        def generator():
            for c in fids:
                yield (c,)
        
        # remove files records
        sql = """delete from files where id = ?"""
        db_cursor.executemany(sql, generator())
        
        # remove tags records
        sql = """delete from tags_files where file_id = ?"""
        db_cursor.executemany(sql, generator())
        
        arg = self.__list_to_string(fids)

        # remove thumbnails
        sql = """select filename from thumbnails where file_id in (%s)""" % arg
        db_cursor.execute(sql)
        res = db_cursor.fetchall()
        if len(res) > 0:
            for fn in res:
                os.unlink(os.path.join(self.internal_dirname, fn[0]))
        
        # remove images
        sql = """select filename, thumbnail from images where file_id in (%s)""" % arg
        db_cursor.execute(sql)
        res = db_cursor.fetchall()
        if len(res) > 0:
            for fn in res:
                if res[0]:
                    os.unlink(os.path.join(self.internal_dirname, fn[0]))
                os.unlink(os.path.join(self.internal_dirname, fn[1]))
        
        # remove thumbs records
        sql = """delete from thumbnails where file_id = ?"""
        db_cursor.executemany(sql, generator())
        
        # remove images records
        sql = """delete from images where file_id = ?"""
        db_cursor.executemany(sql, generator())
        
        # remove gthumb info
        sql = """delete from gthumb where file_id = ?"""
        db_cursor.executemany(sql, generator())
        
        # correct parent direcotry sizes
        # get size and parent of deleting object
        while parent_id:
            sql = """update files set size =
            (select case when
                        sum(size) is null
                    then
                        0
                    else
                        sum(size)
                    end
            from files where parent_id=?) where id=?"""
            db_cursor.execute(sql, (parent_id, parent_id))
            
            sql = """select parent_id from files where id = ? and parent_id!=id"""
            db_cursor.execute(sql, (parent_id,))
            res = db_cursor.fetchone()
            if res:
                parent_id = res[0]
            else:
                parent_id = False
        
        db_connection.commit()
        return
        
    def get_stats(self, selected_id):
        """get statistic information"""
        retval = {}
        if selected_id:
            sql = """select id, type, parent_id from files where id=?"""
            self.db_cursor.execute(sql, (selected_id,))
            res = self.db_cursor.fetchone()
            if not res:
                return retval
        
            selected_item = {'id':res[0], 'type':res[1], 'parent': res[2]}
            
            # collect all parent_id's
            parents = []
            def _recurse(fid):
                parents.append(fid)
                sql = """select id from files where type=? and parent_id=? and parent_id!=1"""
                self.db_cursor.execute(sql, (self.DIR, fid))
                res = self.db_cursor.fetchall()
                if res:
                    for row in res:
                        _recurse(row[0])
            _recurse(selected_id)
            
            if selected_item['parent'] == 1:
                parents.pop(0)
                retval['discs'] = 1
            retval['dirs'] = len(parents)
            
            parents.append(selected_id)
            
            files_count = 0
            
            for p in parents:
                sql = """select count(id) from files where type!=0 and type!=1 and parent_id=?"""
                self.db_cursor.execute(sql, (p,))
                res = self.db_cursor.fetchone()
                if res:
                    files_count+=res[0]
            retval['files'] = files_count
            sql = """select size from files where id=?"""
            self.db_cursor.execute(sql, (selected_id,))
            res = self.db_cursor.fetchone()
            if res:
                retval['size'] = self.__bytes_to_human(res[0])
        else:
            sql = """select count(id) from files where parent_id=1 and type=1"""
            self.db_cursor.execute(sql)
            res = self.db_cursor.fetchone()
            if res:
                retval['discs'] = res[0]
                
            sql = """select count(id) from files where parent_id!=1 and type=1"""
            self.db_cursor.execute(sql)
            res = self.db_cursor.fetchone()
            if res:
                retval['dirs'] = res[0]
                
            sql = """select count(id) from files where parent_id!=1 and type!=1"""
            self.db_cursor.execute(sql)
            res = self.db_cursor.fetchone()
            if res:
                retval['files'] = res[0]
        
            sql = """select sum(size) from files where parent_id=1 and type=1"""
            self.db_cursor.execute(sql)
            res = self.db_cursor.fetchone()
            if res:
                retval['size'] = self.__bytes_to_human(res[0])
        return retval
        
    def get_image_path(self, img_id):
        """return image location"""
        sql = """select filename from images where id=?"""
        self.db_cursor.execute(sql, (img_id,))
        res = self.db_cursor.fetchone()
        if res:
            if res[0]:
                return os.path.join(self.internal_dirname, res[0])
        return None
        
    def update_desc_and_note(self, id, desc='', note=''):
        """update note and description"""
        sql = """UPDATE files SET description=?, note=? WHERE id=?"""
        self.db_cursor.execute(sql, (desc, note, id))
        return
        
    # private class functions
    def __bytes_to_human(self, integer):
        if integer <= 0 or integer < 1024:
            return "%d bytes" % integer
        
        ## convert integer into string with thousands' separator
        #for i in range(len(str(integer))/3+1):
        #    if i == 0:
        #        s_int = str(integer)[-3:]
        #    else:
        #        s_int = str(integer)[-(3*int(i)+3):-(3*int(i))] + " " + s_int
        
        t = integer
        for power in ['kB', 'MB', 'GB', 'TB']:
            t = t /1024.0
            if t < 1 or t < 1024:
                break
        return "%0.2f %s (%d bytes)" % (t, power, integer)
        
    def __clear_trees(self):
        self.__clear_files_tree()
        self.__clear_discs_tree()
    
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
        except IOError, (errno, strerror):
            print "m_main.py: __create_internal_dirname(): ", strerror
        return
    
    def __compress_and_save(self):
        try:
            if self.config.confd['compress']:
                tar = tarfile.open(self.filename, "w:gz")
            else:
                tar = tarfile.open(self.filename, "w")
            if __debug__:
                print "m_main.py: __compress_and_save(): tar open successed"
                
        except IOError, (errno, strerror):
            return False, strerror
        
        os.chdir(self.internal_dirname)
        tar.add('.')
        tar.close()
            
        self.unsaved_project = False
        return True, None
    
    def __create_database(self):
        """make all necessary tables in db file"""
        self.db_cursor.execute("""create table 
                               files(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     parent_id INTEGER,
                                     filename TEXT,
                                     filepath TEXT,
                                     date datetime,
                                     size INTEGER,
                                     type INTEGER,
                                     source INTEGER,
                                     note TEXT,
                                     description TEXT);""")
        self.db_cursor.execute("""create table 
                               tags(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    group_id INTEGER,
                                    tag TEXT);""")
        self.db_cursor.execute("""create table 
                               tags_files(file_id INTEGER,
                                          tag_id INTEGER);""")
        self.db_cursor.execute("""create table 
                               groups(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      name TEXT,
                                      color TEXT);""")
        self.db_cursor.execute("""create table 
                               thumbnails(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                          file_id INTEGER,
                                          filename TEXT);""")
        self.db_cursor.execute("""create table 
                               images(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      file_id INTEGER,
                                      thumbnail TEXT,
                                      filename TEXT);""")
        self.db_cursor.execute("""create table 
                               exif(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    file_id INTEGER,
                                    camera TEXT,
                                    date TEXT,
                                    aperture TEXT,
                                    exposure_program TEXT,
                                    exposure_bias TEXT,
                                    iso TEXT,
                                    focal_length TEXT,
                                    subject_distance TEXT,
                                    metering_mode TEXT,
                                    flash TEXT,
                                    light_source TEXT,
                                    resolution TEXT,
                                    orientation TEXT);""")
        self.db_cursor.execute("""create table 
                               gthumb(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      file_id INTEGER,
                                      note TEXT,
                                      place TEXT,
                                      date datetime);""")
        self.db_cursor.execute("insert into files values(1, 1, 'root', null, 0, 0, 0, 0, null, null);")
        self.db_cursor.execute("insert into groups values(1, 'default', 'black');")
        self.db_connection.commit()
        
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
            
            myit = self.discs_tree.append(discs_tree_iter, None)
            
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
                root, dirs, files = os.walk(path).next()
            except:
                if __debug__:
                    print "m_main.py: cannot access ", path
                #return -1
                return 0
                
            #############
            # directories
            for i in dirs:
                j = self.__decode_filename(i)
                current_dir = os.path.join(root, i)
                
                try:
                    st = os.stat(current_dir)
                    st_mtime = st.st_mtime
                except OSError:
                    st_mtime = 0
                    
                # do NOT follow symbolic links
                if os.path.islink(current_dir):
                    l = self.__decode_filename(os.readlink(current_dir))
                        
                    sql = """
                    insert into files(parent_id, filename, filepath, date, size, type)
                    values(?,?,?,?,?,?)
                    """
                    db_cursor.execute(sql, (currentid, j + " -> " + l,
                                            ocurrent_dir, st_mtime, 0,
                                            self.LIN))
                    dirsize = 0
                else:
                    dirsize = __recurse(currentid, j, current_dir,
                                        st_mtime, 0, self.DIR, myit)
                
                if dirsize == -1:
                    break
                else:
                    _size = _size + dirsize
            
            ########
            # files:
            for i in files:
                if self.abort:
                    break
                
                self.count = self.count + 1
                current_file = os.path.join(root, i)
                
                try:
                    st = os.stat(current_file)
                    st_mtime = st.st_mtime
                    st_size = st.st_size
                except OSError:
                    st_mtime = 0
                    st_size = 0
                    
                _size = _size + st_size
                j = self.__decode_filename(i)
                    
                # do NOT follow symbolic links
                if os.path.islink(current_file):
                    l = self.__decode_filename(os.readlink(current_file))
                    sql = """insert into files(parent_id, filename, filepath,
                                               date, size, type)
                    values(?,?,?,?,?,?)"""
                    db_cursor.execute(sql, (currentid, j + " -> " + l,
                                            current_file, st_mtime, 0,
                                            self.LIN))
                else:
                    sql = """
                    insert into files(parent_id, filename, filepath, date, size, type)
                    values(?,?,?,?,?,?)
                    """
                    db_cursor.execute(sql, (currentid, j, current_file,
                                            st_mtime, st_size, self.FIL))
                    
                    if self.count % 32 == 0:
                        update = True
                    else:
                        update = False
                        
                    ###########################
                    # fetch details about files
                    if self.config.confd['retrive']:
                        update = True
                        exif = None
                        
                        sql = """select seq FROM sqlite_sequence WHERE name='files'"""
                        db_cursor.execute(sql)
                        fileid = db_cursor.fetchone()[0]
                        
                        ext = i.split('.')[-1].lower()
                        
                        # Images - thumbnails and exif data
                        if self.config.confd['thumbs'] and ext in self.IMG:
                            tpath, exif, ret_code = Thumbnail(current_file, base=self.internal_dirname).save(fileid)
                            if ret_code != -1:
                                sql = """insert into thumbnails(file_id, filename) values (?, ?)"""
                                db_cursor.execute(sql, (fileid,
                                                        tpath.split(self.internal_dirname)[1][1:]))
                                
                        # exif - stroe data in exif table
                        if self.config.confd['exif'] and ext in ['jpg', 'jpeg']:
                            p = None
                            if self.config.confd['thumbs'] and exif:
                                p = ParseExif(exif_dict=exif)
                            else:
                                p = ParseExif(exif_file=current_file)
                                if not p.exif_dict:
                                    p = None
                            if p:
                                p = p.parse()
                                p = list(p)
                                p.insert(0, fileid)
                                sql = """INSERT INTO exif (file_id,
                                                           camera,
                                                           date,
                                                           aperture,
                                                           exposure_program,
                                                           exposure_bias,
                                                           iso,
                                                           focal_length,
                                                           subject_distance,
                                                           metering_mode,
                                                           flash,
                                                           light_source,
                                                           resolution,
                                                           orientation)
                                values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                                db_cursor.execute(sql, (tuple(p)))
                            
                        # gthumb - save comments from gThumb program
                        if self.config.confd['gthumb']:
                            gt = GthumbCommentParser(root, i)
                            cmnts = gt.parse()
                            if cmnts:
                                sql = """insert into gthumb(file_id,
                                                            note,
                                                            place,
                                                            date)
                                values(?,?,?,?)"""
                                db_cursor.execute(sql, (fileid,
                                                        cmnts['note'],
                                                        cmnts['place'],
                                                        cmnts['date']
                                                        ))
                                if cmnts.has_key('keywords'):
                                    # TODO: add gthumb keywords to tags and group 'gthumb'
                                    pass
                            
                        
                        # Extensions - user defined actions
                        if ext in self.config.confd['extensions'].keys():
                            cmd = self.config.confd['extensions'][ext]
                            arg = string.replace(current_file, '"', '\\"')
                            output = os.popen(cmd % arg).readlines()
                            desc = ''
                            for line in output:
                                desc += line
                            #desc = string.replace(desc, "\n", "\\n")
                            sql = """update files set description=? where id=?"""
                            db_cursor.execute(sql, (desc, fileid))
                            
                        #if i.split('.').[-1].lower() in mov_ext:
                            # # video only
                            # info = filetypeHelper.guess_video(os.path.join(root,i))
                        ### end of scan
                if update:
                    self.statusmsg = "Scannig: %s" % current_file
                    self.progress = step * self.count
                    
            sql = """update files set size=? where id=?"""
            db_cursor.execute(sql,(_size, currentid))
            if self.abort:
                return -1
            else:
                return _size
        
        if __recurse(1, self.label, self.path, 0, 0, self.DIR) == -1:
            if __debug__:
                print "m_main.py: __scan() __recurse()",
                print "interrupted self.abort = True"
            self.discs_tree.remove(self.fresh_disk_iter)
            db_cursor.close()
            db_connection.rollback()
        else:
            if __debug__:
                print "m_main.py: __scan() __recurse() goes without interrupt"
            if self.currentid:
                if __debug__:
                    print "m_main.py: __scan() removing old branch"
                self.statusmsg = "Removing old branch..."
                self.delete(self.currentid, db_cursor, db_connection)
                
                self.currentid = None
                
            db_cursor.close()
            db_connection.commit()
        db_connection.close()
        if __debug__:
            print "m_main.py: __scan() time: ", (datetime.now() - timestamp)
        
        self.busy = False
        
        # refresh discs tree
        self.__fetch_db_into_treestore()
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
        sql = """
        SELECT id, parent_id, filename FROM files 
        WHERE type=1 ORDER BY parent_id, filename
        """
        db_cursor.execute(sql)
        data = db_cursor.fetchall()
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
            print "m_main.py: __fetch_db_into_treestore() tree generation time: ", (datetime.now() - start_date)
        db_connection.close()
        return
        
    def __append_added_volume(self):
        """append branch from DB to existing tree model"""
        #connect
        db_connection = sqlite.connect("%s" %
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
            print "m_main.py: __append_added_volume() tree generation time: ", (datetime.now() - start_date)
        db_connection.close()
        return
        
    def __decode_filename(self, txt):
        if self.fsenc:
            return txt.decode(self.fsenc)
        else:
            return txt
        
    def __list_to_string(self, array):
        arg =''
        for c in array:
            if len(arg) > 0:
                arg+=", %d" % c
            else:
                arg = "%d" % c
        return arg
    pass # end of class
