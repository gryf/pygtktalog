"""
    Project: pyGTKtalog
    Description: Filesystem scan and file automation layer
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2011-03-27
"""
import os
import sys
import re
from datetime import datetime
import mimetypes

import pygtktalog.misc
from pygtktalog.dbobjects import File, Image, Thumbnail, Config, TYPE
from pygtktalog.dbcommon import Session
from pygtktalog.logger import get_logger
from pygtktalog.video import Video


LOG = get_logger(__name__)
PAT = re.compile("(\[[^\]]*\]"
                 ".*\(\d\d\d\d\))"
                 "\s[^\[]*\[.{8}\]"
                 ".[a-zA-Z0-9]*$")

#PAT = re.compile(r'(?P<group>\[[^\]]*\]\s)?'
#                 r'(?P<title>.*)\s'
#                 r'(?P<year>\(\d{4}\))\s'
#                 r'(?P<kind>.*)'
#                 r'(?P<checksum>\[[A-Z0-9]{8}\])'
#                 r'\.(?P<extension>(avi|asf|mpeg|mpg|mp4|ogm|ogv|mkv|mov|wmv'
#                 r'|rm|rmvb|flv|jpg|png|gif|nfo))\.?(conf)?$')


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
            @path - string with path to be added to topmost node (root)
        """
        self.abort = False
        self.path = path.rstrip(os.path.sep)
        self._files = []
        self._existing_files = []  # for re-use purpose in adding
        self._existing_branch = []  # for branch storage, mainly for updating
        self._session = Session()
        self.files_count = self._get_files_count()
        self.current_count = 0

        self._set_image_path()

    def add_files(self, engine=None):
        """
        Returns list, which contain object, modification date and file
        size.
        """
        self._files = []
        self._existing_branch = []
        LOG.debug("given path: %s", self.path)

        # See, if file exists. If not it would raise OSError exception
        os.stat(self.path)

        if not os.access(self.path, os.R_OK | os.X_OK) \
                or not os.path.isdir(self.path):
            raise NoAccessError("Access to %s is forbidden" % self.path)

        directory = os.path.basename(self.path)
        path = os.path.dirname(self.path)

        if not self._recursive(None, directory, path, 0):
            return None

        # add only first item from _files, because it is a root of the other,
        # so other will be automatically added aswell.
        self._session.add(self._files[0])
        self._session.commit()
        return self._files

    def get_all_children(self, node_id, engine):
        """
        Get children by pure SQL

        Starting from sqlite 3.8.3 it is possile to do this operation as a
        one query using WITH statement. For now on it has to be done in
        application.
        """
        SQL = "select id from files where parent_id=? and type=1"
        SQL2 = "select id from files where parent_id in (%s)"

        row = ((node_id,),)
        all_ids = []
        def req(obj):
            for line in obj:
                all_ids.append(line[0])
                res = engine.execute(SQL, (line[0],)).fetchall()
                if res:
                    req(res)

        req(row)

        sql = SQL2 % ",".join("?" * len(all_ids))
        all_ids = [row_[0] for row_ in engine
                   .execute(sql, tuple(all_ids))
                   .fetchall()]

        all_obj = []
        # number of objects to retrieve at once. Limit is 999. Let's do a
        # little bit below.
        no = 900
        steps = len(all_ids) / no + 1
        for step in range(steps):
            all_obj.extend(self._session
                           .query(File)
                           .filter(File.id
                                   .in_(all_ids[step * no:step * no + no]))
                           .all())
        return all_obj

    def update_files(self, node_id, engine=None):
        """
        Updtate DB contents of provided node.
        """
        self.current_count = 0
        old_node = self._session.query(File).get(node_id)
        if old_node is None:
            LOG.warning("No such object in db: %s", node_id)
            return
        parent = old_node.parent

        self._files = []

        if engine:
            LOG.debug("Getting all File objects via SQL")
            self._existing_branch = self.get_all_children(node_id, engine)
        else:
            LOG.debug("Getting all File objects via ORM (yeah, it SLOW)")
            self._existing_branch = old_node.get_all_children()

        self._existing_branch.insert(0, old_node)

        # Break the chain of parent-children relations
        LOG.debug("Make them orphans")
        for fobj in self._existing_branch:
            fobj.parent = None

        update_path = os.path.join(old_node.filepath, old_node.filename)
        # gimme a string. unicode can't handle strange filenames in paths, so
        # in case of such, better get me a byte string. It is not perfect
        # though, since it WILL crash if the update_path would contain some
        # unconvertable characters.
        update_path = update_path.encode("utf-8")

        # refresh objects
        LOG.debug("Refreshing objects")
        self._get_all_files()

        LOG.debug("path for update: %s", update_path)

        # See, if file exists. If not it would raise OSError exception
        os.stat(update_path)

        if not os.access(update_path, os.R_OK | os.X_OK) \
                or not os.path.isdir(update_path):
            LOG.error("Access to %s is forbidden", update_path)
            raise NoAccessError("Access to %s is forbidden", update_path)

        directory = os.path.basename(update_path)
        path = os.path.dirname(update_path)

        if not self._recursive(parent, directory, path, 0):
            return None

        # update branch
        #self._session.merge(self._files[0])
        LOG.debug("Deleting objects whitout parent: %s",
                  str(self._session.query(File)
                      .filter(File.parent==None).all()))
        self._session.query(File).filter(File.parent==None).delete()

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
                    size += os.lstat(os.path.join(root, fname)).st_size
                except OSError:
                    LOG.warning("Cannot access file %s",
                                os.path.join(root, fname))
        LOG.debug("_get_dirsize, %s: %d", path, size)
        return size

    def _gather_information(self, fobj):
        """
        Try to guess type and gather information about File object if possible
        """
        mimedict = {'audio': self._audio,
                    'video': self._video,
                    'image': self._image}
        extdict = {'.mkv': 'video',  # TODO: move this to config/plugin(?)
                   '.rmvb': 'video',
                   '.ogm': 'video',
                   '.ogv': 'video'}

        fp = os.path.join(fobj.filepath.encode(sys.getfilesystemencoding()),
                          fobj.filename.encode(sys.getfilesystemencoding()))

        mimeinfo = mimetypes.guess_type(fp)
        if mimeinfo[0]:
            mimeinfo = mimeinfo[0].split("/")[0]

        ext = os.path.splitext(fp)[1]

        if mimeinfo and mimeinfo in mimedict.keys():
            mimedict[mimeinfo](fobj, fp)
        elif ext and ext in extdict:
            mimedict[extdict[ext]](fobj, fp)
        else:
            LOG.debug("Filetype not supported %s %s", str(mimeinfo), fp)
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
        result = PAT.search(fobj.filename)
        if result:
            self._check_related(fobj, result.groups()[0])

        vid = Video(filepath)

        fobj.description = vid.get_formatted_tags()

        preview_fn = vid.capture()
        if preview_fn:
            Image(preview_fn, self.img_path, fobj)

    def _check_related(self, fobj, pattern):
        """
        Try to search for related files which belongs to specified File
        object and pattern. If found, additional objects are created.
        """
        for filen in os.listdir(fobj.filepath):
            if pattern in filen and \
                    os.path.splitext(filen)[1] in (".jpg", ".png", ".gif"):
                full_fname = os.path.join(fobj.filepath, filen)
                LOG.debug('found cover file: %s', full_fname)

                Image(full_fname, self.img_path, fobj, False)

                if not fobj.thumbnail:
                    Thumbnail(full_fname, self.img_path, fobj)

    def _name_matcher(self, fpath, fname, media=False):
        """
        Try to match special pattern to filename which may be looks like this:
            [aXXo] Batman (1989) [D3ADBEEF].avi
            [aXXo] Batman (1989) [D3ADBEEF].avi.conf
            [aXXo] Batman (1989) cover [BEEFD00D].jpg
            [aXXo] Batman (1989) cover2 [FEEDD00D].jpg
            [aXXo] Batman (1989) trailer [B00B1337].avi
        or
            Batman (1989) [D3ADBEEF].avi (and so on)

        For media=False it will return True for filename, that matches
        pattern, and there are at least one corresponding media files (avi,
        mpg, mov and so on) _in case the filename differs from media_. This is
        usfull for not storing covers, nfo, conf files in the db.

        For kind == 2 it will return all images and other files that should be
        gather due to video file examinig as a dict of list (conf, nfo and
        images).
        """
        # TODO: dokonczyc to na podstawie tego cudowanego patternu u gory.
        return

    def _get_all_files(self):
        self._existing_files = self._session.query(File).all()

    def _mk_file(self, fname, path, parent, ftype=TYPE['file']):
        """
        Create and return File object
        """
        fullpath = os.path.join(path, fname)

        fname = fname.decode(sys.getfilesystemencoding(),
                             errors="replace")
        path = path.decode(sys.getfilesystemencoding(),
                           errors="replace")

        if ftype == TYPE['link']:
            fname = fname + " -> " + os.readlink(fullpath)

        fob = {'filename': fname,
               'path': path,
               'ftype': ftype}
        try:
            fob['date'] = datetime.fromtimestamp(os.stat(fullpath).st_mtime)
            fob['size'] = os.stat(fullpath).st_size
        except OSError:
            # in case of dead softlink, we will have no time and size
            fob['date'] = None
            fob['size'] = 0

        fobj = self._get_old_file(fob, ftype)

        if fobj:
            LOG.debug("found existing file in db: %s", str(fobj))
            fobj.size = fob['size']  # TODO: update whole tree sizes (for directories/discs)
            fobj.filepath = fob['path']
            fobj.type = fob['ftype']
        else:
            fobj = File(**fob)
            # SLOW. Don't do this. Checksums has no value eventually
            # fobj.mk_checksum()

        if parent is None:
            fobj.parent_id = 1
        else:
            fobj.parent = parent

        self._files.append(fobj)

        return fobj

    def _non_recursive(self, parent, fname, path, size):
        """
        Do the walk through the file system. Non recursively, since it's
        slow as hell.
        @Arguments:
            @parent - directory File object which is parent for the current
                      scope
            @fname - string that hold filename
            @path - full path for further scanning
            @size - size of the object
        """
        fullpath = os.path.join(path, fname)
        parent = self._mk_file(fname, path, parent, TYPE['dir'])
        parent.size = 0
        parent.type = TYPE['dir']

        for root, dirs, files in os.walk(fullpath):
            for dir_ in dirs:
                pass

            for file_ in files:
                self.current_count += 1
                stat = os.lstat(os.path.join(root, file_))
                parent.size += stat.st_size

        # TODO: finish that up

    def _recursive(self, parent, fname, path, size):
        """
        Do the walk through the file system
        @Arguments:
            @parent - directory File object which is parent for the current
                      scope
            @fname - string that hold filename
            @path - full path for further scanning
            @size - size of the object
        """
        if self.abort:
            return False

        fullpath = os.path.join(path, fname)

        parent = self._mk_file(fname, path, parent, TYPE['dir'])

        parent.size = self._get_dirsize(fullpath)
        parent.type = TYPE['dir']

        LOG.info("Scanning `%s' [%s/%s]", fullpath, self.current_count,
                 self.files_count)

        root, dirs, files = os.walk(fullpath).next()
        for fname in files:
            fpath = os.path.join(root, fname)
            self.current_count += 1
            LOG.debug("Processing %s [%s/%s]", fname, self.current_count,
                      self.files_count)

            result = PAT.search(fname)
            test_ = False

            if result and os.path.splitext(fpath)[1] in ('.jpg', '.gif',
                                                         '.png'):
                newpat = result.groups()[0]
                matching_files = []
                for fn_ in os.listdir(root):
                    if newpat in fn_:
                        matching_files.append(fn_)

                if len(matching_files) > 1:
                    LOG.debug('found cover "%s" in group: %s, skipping', fname,
                              str(matching_files))
                    test_ = True
            if test_:
                continue

            if os.path.islink(fpath):
                fob = self._mk_file(fname, root, parent, TYPE['link'])
            else:
                fob = self._mk_file(fname, root, parent)
                existing_obj = self._object_exists(fob)

                if existing_obj:
                    existing_obj.parent = fob.parent
                    fob = existing_obj
                else:
                    LOG.debug("gather information for %s",
                              os.path.join(root, fname))
                    self._gather_information(fob)
                size += fob.size
            if fob not in self._existing_files:
                self._existing_files.append(fob)

        for dirname in dirs:
            dirpath = os.path.join(root, dirname)

            if not os.access(dirpath, os.R_OK|os.X_OK):
                LOG.info("Cannot access directory %s", dirpath)
                continue

            if os.path.islink(dirpath):
                fob = self._mk_file(dirname, root, parent, TYPE['link'])
            else:
                LOG.debug("going into %s", os.path.join(root, dirname))
                self._recursive(parent, dirname, fullpath, size)

        LOG.debug("size of items: %s", parent.size)
        return True

    def _get_old_file(self, fdict, ftype):
        """
        Search for object with provided data in dictionary in stored branch
        (which is updating). Return such object on success, remove it from
        list.
        """
        for index, obj in enumerate(self._existing_branch):
            if ftype == TYPE['link'] and fdict['filename'] == obj.filename:
                return self._existing_branch.pop(index)
            elif fdict['filename'] == obj.filename and \
                    fdict['date'] == obj.date and \
                    ftype == TYPE['file'] and \
                    fdict['size'] in (obj.size, 0):
                obj = self._existing_branch.pop(index)
                obj.size = fdict['size']
                return obj
            elif fdict['filename'] == obj.filename:
                obj = self._existing_branch.pop(index)
                obj.size = fdict['date']
                return obj
        return False

    def _object_exists(self, fobj):
        """
        Perform check if current File object already exists in collection. If
        so, return first matching one, None otherwise.
        """
        for efobj in self._existing_files:
            if efobj.size == fobj.size \
                    and efobj.type == fobj.type \
                    and efobj.date == fobj.date \
                    and efobj.filename == fobj.filename:
                return efobj
        return None

    def _get_files_count(self):
        """return size in bytes"""
        count = 0
        for _, _, files in os.walk(str(self.path)):
            count += len(files)
        LOG.debug("count of files: %s", count)
        return count

    def _set_image_path(self):
        """Get or calculate the images path"""
        image_path = self._session.query(Config) \
                .filter(Config.key=="image_path").one()
        if image_path.value == ":same_as_db:":
            image_path = pygtktalog.misc.calculate_image_path()
        else:
            image_path = pygtktalog.misc.calculate_image_path(image_path.value)

        self.img_path = image_path
