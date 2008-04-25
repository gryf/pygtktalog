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
import shutil
import tarfile
import math

import gtk
import gobject

from gtkmvc.model_mt import ModelMT

from pysqlite2 import dbapi2 as sqlite
from datetime import datetime

import threading as _threading

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

    EXIF_DICT = {0: 'Camera',
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
        """initialize"""
        ModelMT.__init__(self)
        self.unsaved_project = False
        self.filename = None # catalog saved/opened filename
        self.internal_dirname = None
        self.db_connection = None
        self.db_cursor = None
        self.abort = False
        self.source = self.CD
        self.config = ConfigModel()
        self.config.load()
        self.path = None
        self.label = None
        self.currentid = None
        self.thread = None
        self.busy = False
        self.statusmsg = "Idle"
        self.selected_tags = {}

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
        return

    def add_tags(self, fid, tags):
        """add tag (if not exists) and connect it with file"""
        for tag in tags.split(','):
            tag = tag.strip()

            # SQL: first, chek if we already have tag in tags table; get id
            sql = """SELECT id FROM tags WHERE tag = ?"""
            self.db_cursor.execute(sql, (tag, ))
            res = self.db_cursor.fetchone()
            if not res:
                # SQL: insert new tag
                sql = """INSERT INTO tags(tag, group_id)
                VALUES(?, ?)"""
                self.db_cursor.execute(sql, (tag, 1))
                self.db_connection.commit()
                # SQL: get tag id
                sql = """SELECT id FROM tags WHERE tag = ?"""
                self.db_cursor.execute(sql, (tag, ))
                res = self.db_cursor.fetchone()

            tag_id = res[0]

            # SQL: then checkout if file have already tag assigned
            sql = """SELECT file_id FROM tags_files
            WHERE file_id = ? AND tag_id = ?"""
            self.db_cursor.execute(sql, (fid, tag_id))
            res = self.db_cursor.fetchone()
            if not res:
                # SQL: connect tag with file
                sql = """INSERT INTO tags_files(file_id, tag_id)
                VALUES(?, ?)"""
                self.db_cursor.execute(sql, (fid, tag_id))
                self.db_connection.commit()
        self.get_tags()
        return

    def get_tag_by_id(self, tag_id):
        """get tag (string) by its id"""
        # SQL: get tag by id
        sql = """SELECT tag FROM tags WHERE id = ?"""
        self.db_cursor.execute(sql, (int(tag_id), ))
        res = self.db_cursor.fetchone()
        if not res:
            return None
        return res[0]
        
    def get_file_tags(self, file_id):
        """get tags of file"""
        
        # SQL: get tag by id
        sql = """SELECT t.id, t.tag FROM tags t
        LEFT JOIN tags_files f ON t.id=f.tag_id
        WHERE f.file_id = ?
        ORDER BY t.tag"""
        self.db_cursor.execute(sql, (int(file_id), ))
        res = self.db_cursor.fetchall()
        
        tmp = {}
        if len(res) == 0:
            return None
            
        for row in res:
            tmp[row[0]] = row[1]
            
        return tmp
        
    def get_tags(self):
        """fill tags dict with values from db"""
        if not self.selected_tags:
            sql = """SELECT COUNT(f.file_id), t.id, t.tag FROM tags_files f
            LEFT JOIN tags t ON f.tag_id = t.id
            GROUP BY f.tag_id
            ORDER BY t.tag"""
        else:
            id_filter = self.__filter()
            sql = """SELECT COUNT(f.file_id), t.id, t.tag FROM tags_files f
            LEFT JOIN tags t ON f.tag_id = t.id
            WHERE f.file_id in """ + str(tuple(id_filter)) + \
            """GROUP BY f.tag_id
            ORDER BY t.tag"""
            
        self.db_cursor.execute(sql)
        res = self.db_cursor.fetchall()

        if len(res) > 0:
            self.tag_cloud = []
            for row in res:
                self.tag_cloud.append({'id': row[1],
                                      'name': row[2],
                                      'size': row[0],
                                      'count': row[0],
                                      'color':'black'})

        def tag_weight(initial_value):
            """Calculate 'weight' of tag.
            Tags can have sizes between 9 to ~40. Upper size is calculated with
            logarythm and can take in extereme situation around value 55 like
            for 1 milion tags."""
            if not initial_value:
                initial_value = 1
            return 4 * math.log(initial_value, math.e)

        # correct font sizes with tag_weight function.
        count = 0
        for tag0 in self.tag_cloud:
            tmp = int(tag_weight(tag0['size']))
            if tmp == 0:
                tmp = 1
            self.tag_cloud[count]['size'] = tmp + 8
            count += 1
            
    def add_tag_to_path(self, tag_id):
        """add tag to filter"""
        temp = {}
        tag_name = self.get_tag_by_id(tag_id)
        for i in self.selected_tags:
            temp[i] = self.selected_tags[i]
            
        temp[int(tag_id)] = tag_name
        self.selected_tags = temp
        
    def add_image(self, image, file_id, only_thumbs=False):
        """add single image to file/directory"""
        sql = """INSERT INTO images(file_id, thumbnail, filename)
        VALUES(?, null, null)"""
        self.db_cursor.execute(sql, (file_id,))
        self.db_connection.commit()

        sql = """SELECT id FROM images WHERE thumbnail is null
        AND filename IS null AND file_id=?"""
        self.db_cursor.execute(sql, (file_id,))
        res = self.db_cursor.fetchone()
        if res:
            thp, imp, rec = Img(image, self.internal_dirname).save(res[0])
            if rec != -1:
                sql = """UPDATE images SET filename=?,
                thumbnail=? WHERE id=?"""
                if only_thumbs:
                    img = None
                else:
                    img = imp.split(self.internal_dirname)[1][1:]
                self.db_cursor.execute(sql,
                                      (img,
                                       thp.split(self.internal_dirname)[1][1:],
                                       res[0]))
        self.db_connection.commit()

    def del_images(self, file_id):
        """removes images and their thumbnails from selected file/dir"""
        # remove images
        sql = """SELECT filename, thumbnail FROM images WHERE file_id =?"""
        self.db_cursor.execute(sql, (file_id,))
        res = self.db_cursor.fetchall()
        if len(res) > 0:
            for filen in res:
                if filen[0]:
                    os.unlink(os.path.join(self.internal_dirname, filen[0]))
                os.unlink(os.path.join(self.internal_dirname, filen[1]))

        # remove images records
        sql = """DELETE FROM images WHERE file_id = ?"""
        self.db_cursor.execute(sql, (file_id,))
        self.db_connection.commit()

    def delete_image(self, image_id):
        """removes image on specified image id"""
        sql = """SELECT filename, thumbnail FROM images WHERE id=?"""
        self.db_cursor.execute(sql, (image_id,))
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
        sql = """DELETE FROM images WHERE id = ?"""
        self.db_cursor.execute(sql, (image_id,))
        self.db_connection.commit()

    def add_thumbnail(self, img_fn, file_id):
        """generate and add thumbnail to selected file/dir"""
        if self.config.confd['thumbs']:
            self.del_thumbnail(file_id)
            thumb = Thumbnail(img_fn, base=self.internal_dirname)
            retval = thumb.save(file_id)
            if retval[2] != -1:
                path = retval[0].split(self.internal_dirname)[1][1:]
                sql = """insert into thumbnails(file_id, filename)
                values (?, ?)"""
                self.db_cursor.execute(sql, (file_id, path))
                self.db_connection.commit()
                return True
        return False

    def del_thumbnail(self, file_id):
        """removes thumbnail from selected file/dir"""

        # remove thumbnail files
        sql = """SELECT filename FROM thumbnails WHERE file_id=?"""
        self.db_cursor.execute(sql, (file_id,))
        res = self.db_cursor.fetchone()
        if res:
            os.unlink(os.path.join(self.internal_dirname, res[0]))

        # remove thumbs records
        sql = """DELETE FROM thumbnails WHERE file_id=?"""
        self.db_cursor.execute(sql, (file_id,))
        self.db_connection.commit()

    def cleanup(self):
        """remove temporary directory tree from filesystem"""
        self.__close_db_connection()
        if self.internal_dirname != None:
            try:
                shutil.rmtree(self.internal_dirname)
            except OSError:
                pass
        return

    def new(self):
        """create new project"""
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
        except IOError:
            try:
                tar = tarfile.open(filename, "r")
            except IOError:
                self.filename = None
                self.internal_dirname = None
                return

        os.chdir(self.internal_dirname)
        try:
            tar.extractall()
            if __debug__:
                print "m_main.py: extracted tarfile into",
                print self.internal_dirname
        except AttributeError:
            # python's 2.4 tarfile module lacks of method extractall()
            directories = []
            for tarinfo in tar:
                if tarinfo.isdir():
                    # Extract directory with a safe mode, so that
                    # all files below can be extracted as well.
                    try:
                        os.makedirs(os.path.join('.', tarinfo.name), 0700)
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
                try:
                    os.chown(os.path.join('.', tarinfo.name), t.uid)
                    os.utime(os.path.join('.', tarinfo.name), (0, t.mtime))
                except OSError:
                    if __debug__:
                        print "m_main.py: open(): setting corrext owner,",
                        print "mtime etc"
        tar.close()

        self.__connect_to_db()
        self.__fetch_db_into_treestore()
        self.config.add_recent(filename)
        self.get_tags()
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

    def rename(self, file_id, new_name=None):
        """change name of selected object id"""
        if new_name:
            self.db_cursor.execute("update files set filename=? \
                                   WHERE id=?", (new_name, file_id))
            self.db_connection.commit()
            self.__fetch_db_into_treestore()
            self.unsaved_project = True
        else:
            if __debug__:
                print "m_main.py: rename(): no label defined"
        return

    def refresh_discs_tree(self):
        """re-fetch discs tree"""
        self.__fetch_db_into_treestore()

    def get_root_entries(self, parent_id):
        """Get all children down from sepcified root"""
        self.__clear_files_tree()
        
        # directories first
        if not self.selected_tags:
            sql = """SELECT id, filename, size, date FROM files
                WHERE parent_id=? AND type=1
                ORDER BY filename"""
        else:
            id_filter = self.__filter()
            if id_filter != None:
                sql = """SELECT id, filename, size, date FROM files
                WHERE parent_id=? AND type=1 AND id in """ + \
                str(tuple(id_filter)) + """ ORDER BY filename"""
            else:
                sql="""SELECT id, filename, size, date FROM files
                WHERE 1=0"""
                
        
        self.db_cursor.execute(sql, (parent_id,))
        data = self.db_cursor.fetchall()
        for row in data:
            myiter = self.files_list.insert_before(None, None)
            self.files_list.set_value(myiter, 0, row[0])
            self.files_list.set_value(myiter, 1, row[1])
            self.files_list.set_value(myiter, 2, row[2])
            self.files_list.set_value(myiter, 3,
                                      datetime.fromtimestamp(row[3]))
            self.files_list.set_value(myiter, 4, 1)
            self.files_list.set_value(myiter, 5, 'direktorja')
            self.files_list.set_value(myiter, 6, gtk.STOCK_DIRECTORY)

        # all the rest
        if not self.selected_tags:
            sql = """SELECT f.id, f.filename, f.size, f.date, f.type
            FROM files f
            WHERE f.parent_id=? AND f.type!=1
            ORDER BY f.filename"""
        else:
            if id_filter != None:
                sql = """SELECT f.id, f.filename, f.size, f.date, f.type
                FROM files f
                WHERE f.parent_id=? AND f.type!=1 AND id IN """ + \
                str(tuple(id_filter)) + """ ORDER BY f.filename"""
            else:
                sql="""SELECT f.id, f.filename, f.size, f.date, f.type
                FROM files f
                WHERE 1=0"""
                
        
        self.db_cursor.execute(sql, (parent_id,))
        data = self.db_cursor.fetchall()
        for row in data:
            myiter = self.files_list.insert_before(None, None)
            self.files_list.set_value(myiter, 0, row[0])
            self.files_list.set_value(myiter, 1, row[1])
            self.files_list.set_value(myiter, 2, row[2])
            self.files_list.set_value(myiter, 3,
                                      datetime.fromtimestamp(row[3]))
            self.files_list.set_value(myiter, 4, row[4])
            self.files_list.set_value(myiter, 5, 'kategoria srategoria')
            if row[4] == self.FIL:
                self.files_list.set_value(myiter, 6, gtk.STOCK_FILE)
            elif row[4] == self.LIN:
                self.files_list.set_value(myiter, 6, gtk.STOCK_INDEX)
        return

    def get_parent_discs_value(self, child_id):
        """get root id from specified child"""
        if child_id:
            sql = """SELECT parent_id FROM files WHERE id=?"""
            self.db_cursor.execute(sql, (child_id,))
            res = self.db_cursor.fetchone()
            if res:
                return res[0]
        return None

    def get_file_info(self, file_id):
        """get file info from database"""
        retval = {}
        sql = """SELECT f.filename, f.date, f.size, f.type,
                        t.filename, f.description, f.note
                FROM files f
                LEFT JOIN thumbnails t ON t.file_id = f.id
                WHERE f.id = ?"""
        self.db_cursor.execute(sql, (file_id,))
        res = self.db_cursor.fetchone()
        if res:
            retval['debug'] = {'id': file_id,
            'date': datetime.fromtimestamp(res[1]),
            'size': res[2], 'type': res[3]}

            retval['filename'] = res[0]

            if res[5]:
                retval['description'] = res[5]

            if res[6]:
                retval['note'] = res[6]

            if res[4]:
                path = os.path.join(self.internal_dirname, res[4])
                retval['thumbnail'] = path

        sql = """SELECT id, thumbnail FROM images
                WHERE file_id = ?"""
        self.db_cursor.execute(sql, (file_id,))
        res = self.db_cursor.fetchall()
        if res:
            self.images_store = gtk.ListStore(gobject.TYPE_INT, gtk.gdk.Pixbuf)
            for idi, thb in res:
                img = os.path.join(self.internal_dirname, thb)
                pix = gtk.gdk.pixbuf_new_from_file(img)
                self.images_store.append([idi, pix])
            retval['images'] = True

        sql = """SELECT camera, date, aperture, exposure_program,
        exposure_bias, iso, focal_length, subject_distance, metering_mode,
        flash, light_source, resolution, orientation
        FROM exif
        WHERE file_id = ?"""
        self.db_cursor.execute(sql, (file_id,))
        res = self.db_cursor.fetchone()

        if res:
            self.exif_list = gtk.ListStore(gobject.TYPE_STRING,
                                           gobject.TYPE_STRING)
            for key in self.EXIF_DICT:
                myiter = self.exif_list.insert_before(None, None)
                self.exif_list.set_value(myiter, 0, self.EXIF_DICT[key])
                self.exif_list.set_value(myiter, 1, res[key])
            retval['exif'] = True

        # gthumb
        sql = """SELECT note, place, date FROM gthumb WHERE file_id = ?"""
        self.db_cursor.execute(sql, (file_id,))
        res = self.db_cursor.fetchone()

        if res:
            retval['gthumb'] = {'note': res[0],
                                'place': res[1],
                                'date': res[2]}

        return retval

    def get_source(self, path):
        """get source of top level directory"""
        bid = self.discs_tree.get_value(self.discs_tree.get_iter(path[0]), 0)
        sql = """SELECT source FROM files WHERE id = ?"""
        self.db_cursor.execute(sql,
                               (bid,))
        res = self.db_cursor.fetchone()
        if res == None:
            return False
        return int(res[0])

    def get_label_and_filepath(self, path):
        """get source of top level directory"""
        bid = self.discs_tree.get_value(self.discs_tree.get_iter(path), 0)
        sql = """SELECT filepath, filename FROM files
                WHERE id = ? AND parent_id = 1"""
        self.db_cursor.execute(sql, (bid,))
        res = self.db_cursor.fetchone()
        if res == None:
            return None, None
        return res[0], res[1]

    def delete(self, root_id, db_cursor=None, db_connection=None):
        """Remove subtree (item and its children) from main tree, remove tags
        from database remove all possible data, like thumbnails, images, gthumb
        info, exif etc"""

        fids = []

        if not db_cursor:
            db_cursor = self.db_cursor

        if not db_connection:
            db_connection = self.db_connection

        sql = """SELECT parent_id FROM files WHERE id = ?"""
        db_cursor.execute(sql, (root_id,))
        res = db_cursor.fetchone()
        parent_id = res[0]

        def get_children(fid):
            """get children of specified id"""
            fids.append(fid)
            sql = """SELECT id FROM files where parent_id = ?"""
            db_cursor.execute(sql, (fid,))
            res = db_cursor.fetchall()
            if len(res)>0:
                for i in res:
                    get_children(i[0])

        get_children(root_id)

        def generator():
            """simple generator for use in executemany() function"""
            for field in fids:
                yield (field,)

        # remove files records
        sql = """DELETE FROM files WHERE id = ?"""
        db_cursor.executemany(sql, generator())

        # remove tags records
        sql = """DELETE FROM tags_files WHERE file_id = ?"""
        db_cursor.executemany(sql, generator())

        arg = str(tuple(fids))

        # remove thumbnails
        sql = """SELECT filename FROM thumbnails WHERE file_id IN %s""" % arg
        db_cursor.execute(sql)
        res = db_cursor.fetchall()
        if len(res) > 0:
            for row in res:
                os.unlink(os.path.join(self.internal_dirname, row[0]))

        # remove images
        sql = """SELECT filename, thumbnail FROM images
                WHERE file_id IN %s""" % arg
        db_cursor.execute(sql)
        res = db_cursor.fetchall()
        if len(res) > 0:
            for row in res:
                if row[0]:
                    os.unlink(os.path.join(self.internal_dirname, row[0]))
                os.unlink(os.path.join(self.internal_dirname, row[1]))

        # remove thumbs records
        sql = """DELETE FROM thumbnails WHERE file_id = ?"""
        db_cursor.executemany(sql, generator())

        # remove images records
        sql = """DELETE FROM images WHERE file_id = ?"""
        db_cursor.executemany(sql, generator())

        # remove gthumb info
        sql = """DELETE FROM gthumb WHERE file_id = ?"""
        db_cursor.executemany(sql, generator())

        # correct parent direcotry sizes
        # get size and parent of deleting object
        while parent_id:
            sql = """UPDATE files SET size =
            (SELECT CASE WHEN
                        SUM(size) IS null
                    THEN
                        0
                    ELSE
                        SUM(size)
                    END
            FROM files WHERE parent_id=?)
            WHERE id=?"""
            db_cursor.execute(sql, (parent_id, parent_id))

            sql = """SELECT parent_id FROM files
                    WHERE id = ? AND parent_id!=id"""
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
            sql = """SELECT id, type, parent_id FROM files WHERE id=?"""
            self.db_cursor.execute(sql, (selected_id,))
            res = self.db_cursor.fetchone()
            if not res:
                return retval

            selected_item = {'id':res[0], 'type':res[1], 'parent': res[2]}

            # collect all parent_id's
            parents = []

            def _recurse(fid):
                """recursive gather direcotories ids and store it in list"""
                parents.append(fid)
                sql = """SELECT id FROM files
                WHERE type=? AND parent_id=? AND parent_id!=1"""
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

            for parent in parents:
                sql = """SELECT count(id) FROM files
                WHERE type!=0 AND type!=1 AND parent_id=?"""
                self.db_cursor.execute(sql, (parent,))
                res = self.db_cursor.fetchone()
                if res:
                    files_count += res[0]
            retval['files'] = files_count
            sql = """SELECT size FROM files WHERE id=?"""
            self.db_cursor.execute(sql, (selected_id,))
            res = self.db_cursor.fetchone()
            if res:
                retval['size'] = self.__bytes_to_human(res[0])
        else:
            sql = """SELECT count(id) FROM files
            WHERE parent_id=1 AND type=1"""
            self.db_cursor.execute(sql)
            res = self.db_cursor.fetchone()
            if res:
                retval['discs'] = res[0]

            sql = """SELECT count(id) FROM files
                    WHERE parent_id!=1 AND type=1"""
            self.db_cursor.execute(sql)
            res = self.db_cursor.fetchone()
            if res:
                retval['dirs'] = res[0]

            sql = """SELECT count(id) FROM files
                    WHERE parent_id!=1 AND type!=1"""
            self.db_cursor.execute(sql)
            res = self.db_cursor.fetchone()
            if res:
                retval['files'] = res[0]

            sql = """SELECT sum(size) FROM files
                    WHERE parent_id=1 AND type=1"""
            self.db_cursor.execute(sql)
            res = self.db_cursor.fetchone()
            if res:
                retval['size'] = self.__bytes_to_human(res[0])
        return retval

    def get_image_path(self, img_id):
        """return image location"""
        sql = """SELECT filename FROM images WHERE id=?"""
        self.db_cursor.execute(sql, (img_id,))
        res = self.db_cursor.fetchone()
        if res:
            if res[0]:
                return os.path.join(self.internal_dirname, res[0])
        return None

    def update_desc_and_note(self, file_id, desc='', note=''):
        """update note and description"""
        sql = """UPDATE files SET description=?, note=? WHERE id=?"""
        self.db_cursor.execute(sql, (desc, note, file_id))
        return

    # private class functions
    def __bytes_to_human(self, integer):
        """return integer digit in human readable string representation"""
        if integer <= 0 or integer < 1024:
            return "%d bytes" % integer

        ## convert integer into string with thousands' separator
        #for i in range(len(str(integer))/3+1):
        #    if i == 0:
        #        s_int = str(integer)[-3:]
        #    else:
        #        s_int = str(integer)[-(3*int(i)+3):-(3*int(i))] + " " + s_int
        power = None
        temp = integer
        for power in ['kB', 'MB', 'GB', 'TB']:
            temp = temp /1024.0
            if temp < 1 or temp < 1024:
                break
        return "%0.2f %s (%d bytes)" % (temp, power, integer)

    def __clear_trees(self):
        """clears treemodel and treestore of files and discs tree"""
        self.__clear_files_tree()
        self.__clear_discs_tree()

    def __clear_discs_tree(self):
        """try to clear model for discs"""
        try:
            self.discs_tree.clear()
        except:
            pass

    def __clear_files_tree(self):
        """try to clear store for files/directories"""
        try:
            self.files_list.clear()
        except:
            pass

    def __connect_to_db(self):
        """initialize db connection and store it in class attributes"""
        self.db_connection = sqlite.connect("%s" % \
                    (self.internal_dirname + '/db.sqlite'),
                    detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.db_cursor = self.db_connection.cursor()
        return

    def __close_db_connection(self):
        """close db conection"""
        if self.db_cursor != None:
            self.db_cursor.close()
            self.db_cursor = None
        if self.db_connection != None:
            self.db_connection.close()
            self.db_connection = None
        return

    def __create_internal_dirname(self):
        """create temporary directory for working thumb/image files and
        database"""
        self.cleanup()
        self.internal_dirname = "/tmp/pygtktalog%d" % \
            datetime.now().microsecond
        try:
            os.mkdir(self.internal_dirname)
        except IOError, (errno, strerror):
            print "m_main.py: __create_internal_dirname(): ", strerror
        return

    def __compress_and_save(self):
        """create (and optionaly compress) tar archive from working directory
        and write it to specified file"""
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
        sql = """INSERT INTO files
                VALUES(1, 1, 'root', null, 0, 0, 0, 0, null, null)"""
        self.db_cursor.execute(sql)
        sql = """INSERT INTO groups VALUES(1, 'default', 'black')"""
        self.db_cursor.execute(sql)
        self.db_connection.commit()

        
    def __filter(self):
        """return list of ids of files (AND their parent, even if they have no
        assigned tags) that corresponds to tags"""
        
        filtered_ids = []
        count = 0
        for tid in self.selected_tags:
            temp1 = []
            sql = """SELECT file_id
            FROM tags_files
            WHERE tag_id=? """
            self.db_cursor.execute(sql, (tid, ))
            data = self.db_cursor.fetchall()
            for row in data:
                temp1.append(row[0])
                
            if count > 0:
                filtered_ids = list(set(filtered_ids).intersection(temp1))
            else:
                filtered_ids = temp1
            count += 1
                
        parents = []
        for i in filtered_ids:
            sql = """SELECT parent_id
            FROM files
            WHERE id = ?"""
            self.db_cursor.execute(sql, (i, ))
            data = self.db_cursor.fetchone()
            if data:
                parents.append(data[0])
                while True:
                    sql = """SELECT parent_id
                    FROM files
                    WHERE id = ? and id!=parent_id"""
                    self.db_cursor.execute(sql, (data[0], ))
                    data = self.db_cursor.fetchone()
                    if not data:
                        break
                    else:
                        parents.append(data[0])
                        
        return list(set(parents).union(filtered_ids))
        
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
                self.discs_tree.set_value(myit, 2, gtk.STOCK_CDROM)
                sql = """INSERT INTO
                            files(parent_id, filename, filepath, date,
                                  size, type, source)
                        VALUES(?,?,?,?,?,?,?)"""
                db_cursor.execute(sql, (parent_id, name, path, date, size,
                                        filetype, self.source))
            else:
                self.discs_tree.set_value(myit, 2, gtk.STOCK_DIRECTORY)
                sql = """INSERT INTO
                files(parent_id, filename, filepath, date, size, type)
                VALUES(?,?,?,?,?,?)"""
                db_cursor.execute(sql, (parent_id, name, path,
                                        date, size, filetype))

            sql = """SELECT seq FROM sqlite_sequence WHERE name='files'"""
            db_cursor.execute(sql)
            currentid = db_cursor.fetchone()[0]

            self.discs_tree.set_value(myit, 0, currentid)
            self.discs_tree.set_value(myit, 1, name)
            self.discs_tree.set_value(myit, 3, parent_id)

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

                    sql = """INSERT INTO
                    files(parent_id, filename, filepath, date, size, type)
                    VALUES(?,?,?,?,?,?)"""
                    db_cursor.execute(sql, (currentid, j + " -> " + l,
                                            current_dir, st_mtime, 0,
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
                    sql = """INSERT INTO
                    files(parent_id, filename, filepath, date, size, type)
                    VALUES(?,?,?,?,?,?)"""
                    db_cursor.execute(sql, (currentid, j + " -> " + l,
                                            current_file, st_mtime, 0,
                                            self.LIN))
                else:
                    sql = """INSERT INTO
                    files(parent_id, filename, filepath, date, size, type)
                    VALUES(?,?,?,?,?,?)"""
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

                        sql = """SELECT seq FROM sqlite_sequence
                            WHERE name='files'"""
                        db_cursor.execute(sql)
                        fileid = db_cursor.fetchone()[0]

                        ext = i.split('.')[-1].lower()

                        # Images - thumbnails and exif data
                        if self.config.confd['thumbs'] and ext in self.IMG:
                            t = Thumbnail(current_file,
                                          base=self.internal_dirname)
                            tpath, exif, ret_code = t.save(fileid)
                            if ret_code != -1:
                                sql = """INSERT INTO
                                thumbnails(file_id, filename)
                                VALUES(?, ?)"""
                                t = tpath.split(self.internal_dirname)[1][1:]
                                db_cursor.execute(sql, (fileid, t))

                        # exif - store data in exif table
                        jpg = ['jpg', 'jpeg']
                        if self.config.confd['exif'] and ext in jpg:
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
                                                        cmnts['date']))
                                if 'keywords' in cmnts:
                                    # TODO: add gthumb keywords to tags
                                    pass

                        # Extensions - user defined actions
                        if ext in self.config.confd['extensions'].keys():
                            cmd = self.config.confd['extensions'][ext]
                            arg = current_file.replace('"', '\\"')
                            output = os.popen(cmd % arg).readlines()
                            desc = ''
                            for line in output:
                                desc += line

                            sql = """UPDATE files SET description=?
                                    WHERE id=?"""
                            db_cursor.execute(sql, (desc, fileid))

                        ### end of scan
                if update:
                    self.statusmsg = "Scannig: %s" % current_file
                    self.progress = step * self.count

            sql = """UPDATE files SET size=? WHERE id=?"""
            db_cursor.execute(sql, (_size, currentid))
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
        detect_types = sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES
        db_connection = sqlite.connect("%s" % \
                                       (self.internal_dirname + '/db.sqlite'),
                                       detect_types = detect_types)
        db_cursor = db_connection.cursor()

        # fetch all the directories
        #try:
        if not self.selected_tags:
            sql = """SELECT id, parent_id, filename FROM files
            WHERE type=1 ORDER BY parent_id, filename"""
        else:
            id_filter = self.__filter()
            if id_filter != None:
                sql = """SELECT id, parent_id, filename FROM files
                WHERE type=1 and id in """ + str(tuple(id_filter)) \
                + """ ORDER BY parent_id, filename"""
            else:
                sql="""SELECT id, parent_id, filename FROM files
                WHERE 1=0"""
        db_cursor.execute(sql)
        data = db_cursor.fetchall()
        #except:
        #    # cleanup
        #    self.cleanup()
        #    self.filename = None
        #    self.internal_dirname = None
        #    print "%s: Wrong database format!" % self.filename
        #    return

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
            print "m_main.py: __fetch_db_into_treestore()",
            print "tree generation time: ", (datetime.now() - start_date)
        db_connection.close()
        return

    def __append_added_volume(self):
        """append branch from DB to existing tree model"""
        #connect
        detect_types = sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES
        db_connection = sqlite.connect("%s" %
                                       (self.internal_dirname + '/db.sqlite'),
                                       detect_types = detect_types)
        db_cursor = db_connection.cursor()

        sql = """SELECT id, parent_id, filename FROM files
        WHERE type=1 ORDER BY parent_id, filename"""
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
            print "m_main.py: __append_added_volume() tree generation time: ",
            print datetime.now() - start_date
        db_connection.close()
        return

    def __decode_filename(self, txt):
        """decode filename with encoding taken form ENV, returns unicode
        string"""
        if self.fsenc:
            return txt.decode(self.fsenc)
        else:
            return txt

