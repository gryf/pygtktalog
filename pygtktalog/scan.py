"""
    Project: pyGTKtalog
    Description: Filesystem scan and file automation layer
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2011-03-27
"""
import os
import sys
from datetime import datetime
import mimetypes

from pygtktalog.dbobjects import File, Image
from pygtktalog.dbcommon import Session
from pygtktalog.logger import get_logger
from pygtktalog.video import Video


LOG = get_logger(__name__)


class NoAccessError(Exception):
    pass


class Scan(object):
    """
    Retrieve and identify all files recursively on given path
    """
    def __init__(self, path):
        """
        Initialize
        @Arguments:
            @path - string with initial root directory to scan
        """
        self.abort = False
        self.path = path.rstrip(os.path.sep)
        self._files = []
        self._existing_files = []
        self._session = Session()

    def add_files(self):
        """
        Returns list, which contain object, modification date and file
        size.
        """
        self._files = []
        LOG.debug("given path: %s" % self.path)

        # See, if file exists. If not it would raise OSError exception
        os.stat(self.path)

        if not os.access(self.path, os.R_OK | os.X_OK) \
                or not os.path.isdir(self.path):
            raise NoAccessError("Access to %s is forbidden" % self.path)

        directory = os.path.basename(self.path)
        path = os.path.dirname(self.path)
        if not self._recursive(None, directory, path, 0, 0, 1):
            return None

        # add only first item from _files, because it is a root of the other,
        # so other will be automatically added aswell.
        self._session.add(self._files[0])
        self._session.commit()
        return self._files

    def _get_dirsize(self, path):
        """
        Returns sum of all files under specified path (also in subdirs)
        """

        size = 0

        for root, dirs, files in os.walk(path):
            for fname in files:
                try:
                    size += os.stat(os.path.join(root, fname)).st_size
                except OSError:
                    LOG.info("Cannot access file %s" % \
                            os.path.join(root, fname))

        return size

    def _gather_information(self, fobj):
        """
        Try to guess type and gather information about File object if possible
        """
        mimedict = {'audio': self._audio,
                    'video': self._video,
                    'image': self._image}
        fp = os.path.join(fobj.filepath.encode(sys.getfilesystemencoding()),
                          fobj.filename.encode(sys.getfilesystemencoding()))

        mimeinfo = mimetypes.guess_type(fp)
        if mimeinfo[0] and mimeinfo[0].split("/")[0] in mimedict.keys():
            mimedict[mimeinfo[0].split("/")[0]](fobj, fp)
        else:
            #LOG.info("Filetype not supported " + str(mimeinfo) + " " +  fp)
            pass

    def _audio(self, fobj, filepath):
        #LOG.warning('audio')
        return

    def _image(self, fobj, filepath):
        #LOG.warning('image')
        return

    def _video(self, fobj, filepath):
        """
        Make captures for a movie. Save it under uniq name.
        """
        vid = Video(filepath)

        preview_fn = vid.capture()
        Image(preview_fn, fobj)

    def _get_all_files(self):
        self._existing_files = self._session.query(File).all()

    def _mk_file(self, fname, path, parent):
        """
        Create and return File object
        """
        fullpath = os.path.join(path, fname)

        fname = fname.decode(sys.getfilesystemencoding())
        path = path.decode(sys.getfilesystemencoding())
        fob = File(filename=fname, path=path)
        fob.date = datetime.fromtimestamp(os.stat(fullpath).st_mtime)
        fob.size = os.stat(fullpath).st_size
        fob.parent = parent
        fob.type = 2

        if parent is None:
            fob.parent_id = 1

        self._files.append(fob)
        return fob

    def _recursive(self, parent, fname, path, date, size, ftype):
        """
        Do the walk through the file system
        @Arguments:
            @parent - directory File object which is parent for the current
                      scope
            @fname - string that hold filename
            @path - full path for further scanning
            @date -
            @size - size of the object
            @ftype -
        """
        if self.abort:
            return False

        LOG.debug("args: fname: %s, path: %s" % (fname, path))
        fullpath = os.path.join(path, fname)

        parent = self._mk_file(fname, path, parent)
        parent.size = self._get_dirsize(fullpath)
        parent.type = 1

        self._get_all_files()
        root, dirs, files = os.walk(fullpath).next()
        for fname in files:
            fpath = os.path.join(root, fname)
            fob = self._mk_file(fname, root, parent)
            if os.path.islink(fpath):
                fob.filename = fob.filename + " -> " + os.readlink(fpath)
                fob.type = 3
            else:
                existing_obj = self._object_exists(fob)
                if existing_obj:
                    fob.tags = existing_obj.tags
                    fob.thumbnail = [th.get_copy \
                            for th in existing_obj.thumbnail]
                    fob.images = [img.get_copy() \
                            for img in existing_obj.images]
                else:
                    LOG.debug("gather information")
                    self._gather_information(fob)
                size += fob.size
            self._existing_files.append(fob)

        for dirname in dirs:
            dirpath = os.path.join(root, dirname)

            if not os.access(dirpath, os.R_OK|os.X_OK):
                LOG.info("Cannot access directory %s" % dirpath)
                continue

            if os.path.islink(dirpath):
                fob = self._mk_file(dirname, root, parent)
                fob.filename = fob.filename + " -> " + os.readlink(dirpath)
                fob.type = 3
            else:
                LOG.debug("going into %s" % dirname)
                self._recursive(parent, dirname, fullpath, date, size, ftype)

        LOG.debug("size of items: %s" % parent.size)
        return True

    def _object_exists(self, fobj):
        """
        Perform check if current File object already exists in collection. If
        so, return first matching one, None otherwise.
        """
        for efobj in self._existing_files:
            if efobj.size == fobj.size \
                    and efobj.type == fobj.type \
                    and efobj.date == fobj.date:
                return efobj
        return None

class asdScan(object):
    """
    Retrieve and identify all files recursively on given path
    """
    def __init__(self, path, tree_model):
        LOG.debug("initialization")
        self.path = path
        self.abort = False
        self.label = None
        self.DIR = None
        self.source = None

    def scan(self):
        """
        scan content of the given path
        """
        self.busy = True

        # count files in directory tree
        LOG.info("Calculating number of files in directory tree...")

        step = 0
        try:
            for root, dirs, files in os.walk(self.path):
                step += len(files)
        except Exception, ex:
            LOG.warning("exception on file %s: %s: %s" \
                    % (self.path, ex.__class__.__name__, str(ex)))
            pass

        step = 1 / float(step or 1)

        self.count = 0

        def _recurse(parent_id, name, path, date, size, filetype,
                      discs_tree_iter=None):
            """recursive scans given path"""
            if self.abort:
                return -1

            _size = size

            if parent_id == 1:
                sql = """INSERT INTO
                            files(parent_id, filename, filepath, date,
                                  size, type, source)
                        VALUES(?,?,?,?,?,?,?)"""
                print(sql, (parent_id, name, path, date, size,
                                        filetype, self.source))
            else:
                sql = """INSERT INTO
                files(parent_id, filename, filepath, date, size, type)
                VALUES(?,?,?,?,?,?)"""
                print(sql, (parent_id, name, path,
                                        date, size, filetype))

            sql = """SELECT seq FROM sqlite_sequence WHERE name='files'"""
            print(sql)
            currentid = None  #db_cursor.fetchone()[0]

            try:
                root, dirs, files = os.walk(path).next()
            except:
                LOG.debug("cannot access ", path)
                return 0

            #############
            # directories
            for i in dirs:
                j = i #j = self.__decode_filename(i)
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
                    print(sql, (currentid, j + " -> " + l,
                                            current_dir, st_mtime, 0,
                                            self.LIN))
                    dirsize = 0
                else:
                    myit = None
                    dirsize = _recurse(currentid, j, current_dir,
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
                j = i  #self.__decode_filename(i)

                # do NOT follow symbolic links
                if os.path.islink(current_file):
                    l = self.__decode_filename(os.readlink(current_file))
                    sql = """INSERT INTO
                    files(parent_id, filename, filepath, date, size, type)
                    VALUES(?,?,?,?,?,?)"""
                    print(sql, (currentid, j + " -> " + l,
                                            current_file, st_mtime, 0,
                                            self.LIN))
                else:
                    sql = """INSERT INTO
                    files(parent_id, filename, filepath, date, size, type)
                    VALUES(?,?,?,?,?,?)"""
                    print(sql, (currentid, j, current_file,
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
                        print(sql)
                        fileid = 1  # dummy!

                        ext = i.split('.')[-1].lower()

                        # Video
                        if ext in self.MOV:
                            v = Video(current_file)
                            cfn = v.capture()
                            img = Img(cfn, self.image_path)
                            th = img.save()
                            if th:
                                sql = """INSERT INTO
                                thumbnails(file_id, filename)
                                VALUES(?, ?)"""
                                print(sql, (fileid, th + "_t"))
                                sql = """INSERT INTO images(file_id, filename)
                                VALUES(?, ?)"""
                                print(sql, (fileid, th))
                            os.unlink(cfn)

                        # Images - thumbnails and exif data
                        if self.config.confd['thumbs'] and ext in self.IMG:
                            thumb = Thumbnail(current_file, self.image_path)
                            th, exif = thumb.save()
                            if th:
                                sql = """INSERT INTO
                                thumbnails(file_id, filename)
                                VALUES(?, ?)"""
                                print(sql, (fileid, th))

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
                                print(sql, (tuple(p)))

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
                                print(sql, (fileid,
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
                            print(sql, (desc, fileid))

                        ### end of scan
                if update:
                    self.statusmsg = "Scannig: %s" % current_file
                    self.progress = step * self.count

            sql = """UPDATE files SET size=? WHERE id=?"""
            print(sql, (_size, currentid))
            if self.abort:
                return -1
            else:
                return _size

        if _recurse(1, self.label, self.path, 0, 0, self.DIR) == -1:
            LOG.debug("interrupted self.abort = True")
        else:
            LOG.debug("recursive goes without interrupt")
            if self.currentid:
                LOG.debug("removing old branch")
                self.statusmsg = "Removing old branch..."
                self.currentid = None

        self.busy = False

        # refresh discs tree
        self.statusmsg = "Idle"
        self.progress = 0
        self.abort = False
