"""
    Project: pyGTKtalog
    Description: Definition of DB objects classes. Using SQLAlchemy.
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-07
"""
import os
import errno
import shutil
from hashlib import sha256
from zlib import crc32

from sqlalchemy import Column, Table, Integer, Text
from sqlalchemy import DateTime, ForeignKey, Sequence
from sqlalchemy.orm import relation, backref

from pygtktalog.dbcommon import Base
from pygtktalog.thumbnail import ThumbCreator
from pygtktalog.logger import get_logger


LOG = get_logger(__name__)

IMG_PATH = "/home/gryf/.pygtktalog/imgs2/"  # FIXME: should be configurable

tags_files = Table("tags_files", Base.metadata,
                   Column("file_id", Integer, ForeignKey("files.id")),
                   Column("tag_id", Integer, ForeignKey("tags.id")))

TYPE = {'root': 0, 'dir': 1, 'file': 2, 'link': 3}


def mk_paths(fname):
    #new_name = str(uuid.uuid1()).split("-")
    fd = open(fname)
    new_path = "%x" % (crc32(fd.read(10*1024*1024)) & 0xffffffff)
    fd.close()

    new_path = [new_path[i:i + 2] for i in range(0, len(new_path), 2)]
    full_path = os.path.join(IMG_PATH, *new_path[:-1])

    try:
        os.makedirs(full_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            LOG.debug("Directory %s already exists." % full_path)

    return new_path


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, Sequence("file_id_seq"), primary_key=True)
    parent_id = Column(Integer, ForeignKey("files.id"), index=True)
    filename = Column(Text)
    filepath = Column(Text)
    date = Column(DateTime)
    size = Column(Integer)
    type = Column(Integer, index=True)
    source = Column(Integer)
    note = Column(Text)
    description = Column(Text)
    # checksum = Column(Text)

    children = relation('File',
                        backref=backref('parent', remote_side="File.id"),
                        order_by=[type, filename])
    tags = relation("Tag", secondary=tags_files, order_by="Tag.tag")
    thumbnail = relation("Thumbnail", backref="file")
    images = relation("Image", backref="file", order_by="Image.filename")

    def __init__(self, filename=None, path=None, date=None, size=None,
                 ftype=None, src=None):
        """Create file object with empty defaults"""
        self.filename = filename
        self.filepath = path
        self.date = date
        self.size = size
        self.type = ftype
        self.source = src

    def __repr__(self):
        return "<File('%s', %s)>" % (str(self.filename), str(self.id))

    def get_all_children(self):
        """
        Return list of all node direct and indirect children
        """
        def _recursive(node):
            children = []
            if node.children:
                for child in node.children:
                    children += _recursive(child)
            if node != self:
                children.append(node)

            return children

        if self.children:
            return _recursive(self)
        else:
            return []

    # def mk_checksum(self):
        # if not (self.filename and self.filepath):
            # return

        # full_name = os.path.join(self.filepath, self.filename)

        # SLOW!
        # if os.path.isfile(full_name):
            # fd = open(full_name)
            # self.checksum = sha256(fd.read(10*1024*1024)).hexdigest()
            # fd.close()

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, Sequence("group_id_seq"), primary_key=True)
    name = Column(Text)
    color = Column(Text)

    def __init__(self, name=None, color=None):
        self.name = name
        self.color = color

    def __repr__(self):
        return "<Group('%s', %s)>" % (str(self.name), str(self.id))


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, Sequence("tags_id_seq"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)
    tag = Column(Text)
    group = relation('Group', backref=backref('tags', remote_side="Group.id"))

    files = relation("File", secondary=tags_files)

    def __init__(self, tag=None, group=None):
        self.tag = tag
        self.group = group

    def __repr__(self):
        return "<Tag('%s', %s)>" % (str(self.tag), str(self.id))


class Thumbnail(Base):
    __tablename__ = "thumbnails"
    id = Column(Integer, Sequence("thumbnail_id_seq"), primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"), index=True)
    filename = Column(Text)

    def __init__(self, filename=None, file_obj=None):
        self.filename = filename
        self.file = file_obj
        if filename and file_obj:
            self.save(self.filename)

    def save(self, fname):
        """
        Create file related thumbnail, add it to the file object.
        """
        new_name = mk_paths(fname)
        ext = os.path.splitext(self.filename)[1]
        if ext:
            new_name.append("".join([new_name.pop(), ext]))

        thumb = ThumbCreator(self.filename).generate()
        name, ext = os.path.splitext(new_name.pop())
        new_name.append("".join([name, "_t", ext]))
        self.filename = os.path.sep.join(new_name)
        if not os.path.exists(os.path.join(IMG_PATH, *new_name)):
            shutil.move(thumb, os.path.join(IMG_PATH, *new_name))
        else:
            LOG.info("Thumbnail already exists (%s: %s)" % \
                    (fname, "/".join(new_name)))
            os.unlink(thumb)

    def __repr__(self):
        return "<Thumbnail('%s', %s)>" % (str(self.filename), str(self.id))


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, Sequence("images_id_seq"), primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"), index=True)
    filename = Column(Text)

    def __init__(self, filename=None, file_obj=None, move=True):
        self.filename = None
        self.file = file_obj
        if filename:
            self.filename = filename
            self.save(filename, move)

    def save(self, fname, move=True):
        """
        Save and create coressponding thumbnail (note: it differs from file
        related thumbnail!)
        """
        new_name = mk_paths(fname)
        ext = os.path.splitext(self.filename)[1]

        if ext:
            new_name.append("".join([new_name.pop(), ext]))

        if not os.path.exists(os.path.join(IMG_PATH, *new_name)):
            if move:
                shutil.move(self.filename, os.path.join(IMG_PATH, *new_name))
            else:
                shutil.copy(self.filename, os.path.join(IMG_PATH, *new_name))
        else:
            LOG.warning("Image with same CRC already exists "
                        "('%s', '%s')" % (self.filename, "/".join(new_name)))

        self.filename = os.path.sep.join(new_name)

        name, ext = os.path.splitext(new_name.pop())
        new_name.append("".join([name, "_t", ext]))

        if not os.path.exists(os.path.join(IMG_PATH, *new_name)):
            thumb = ThumbCreator(os.path.join(IMG_PATH, self.filename))
            shutil.move(thumb.generate(), os.path.join(IMG_PATH, *new_name))
        else:
            LOG.info("Thumbnail already generated %s" % "/".join(new_name))


    def get_copy(self):
        """
        Create the very same object as self with exception of id field
        """
        img = Image()
        img.filename = self.filename
        return img

    @property
    def thumbpath(self):
        """
        Return full path to thumbnail of this image
        """
        path, fname = os.path.split(self.filename)
        base, ext = os.path.splitext(fname)
        return os.path.join(IMG_PATH, path, base + "_t" + ext)

    @property
    def imagepath(self):
        """
        Return full path to image
        """
        return os.path.join(IMG_PATH, self.filename)

    def __repr__(self):
        return "<Image('%s', %s)>" % (str(self.filename), str(self.id))


class Exif(Base):
    __tablename__ = "exif"
    id = Column(Integer, Sequence("exif_id_seq"), primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"), index=True)
    camera = Column(Text)
    date = Column(Text)
    aperture = Column(Text)
    exposure_program = Column(Text)
    exposure_bias = Column(Text)
    iso = Column(Text)
    focal_length = Column(Text)
    subject_distance = Column(Text)
    metering_mode = Column(Text)
    flash = Column(Text)
    light_source = Column(Text)
    resolution = Column(Text)
    orientation = Column(Text)

    def __init__(self):
        self.camera = None
        self.date = None
        self.aperture = None
        self.exposure_program = None
        self.exposure_bias = None
        self.iso = None
        self.focal_length = None
        self.subject_distance = None
        self.metering_mode = None
        self.flash = None
        self.light_source = None
        self.resolution = None
        self.orientation = None

    def __repr__(self):
        return "<Exif('%s', %s)>" % (str(self.date), str(self.id))


class Gthumb(Base):
    __tablename__ = "gthumb"
    id = Column(Integer, Sequence("gthumb_id_seq"), primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"), index=True)
    note = Column(Text)
    place = Column(Text)
    date = Column(DateTime)

    def __init__(self, note=None, place=None, date=None):
        self.note = note
        self.place = place
        self.date = date

    def __repr__(self):
        return "<Gthumb('%s', '%s', %s)>" % (str(self.date), str(self.place),
                                             str(self.id))
