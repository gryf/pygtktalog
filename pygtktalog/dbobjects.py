"""
    Project: pyGTKtalog
    Description: Definition of DB objects classes. Using SQLAlchemy.
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-07
"""
import os
from cStringIO import StringIO
from hashlib import sha256

from sqlalchemy import Column, Table, Integer, Text, Binary, \
        DateTime, ForeignKey, Sequence
from sqlalchemy.orm import relation, backref

from pygtktalog.dbcommon import Base
from pygtktalog.thumbnail import ThumbCreator


IMG_PATH = "/home/gryf/.pygtktalog/imgs/"  # FIXME: should be configurable

tags_files = Table("tags_files", Base.metadata,
                   Column("file_id", Integer, ForeignKey("files.id")),
                   Column("tag_id", Integer, ForeignKey("tags.id")))

TYPE = {'root': 0, 'dir': 1, 'file': 2, 'link': 3}

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, Sequence("file_id_seq"), primary_key=True)
    parent_id = Column(Integer, ForeignKey("files.id"))
    filename = Column(Text)
    filepath = Column(Text)
    date = Column(DateTime)
    size = Column(Integer)
    type = Column(Integer)
    source = Column(Integer)
    note = Column(Text)
    description = Column(Text)
    checksum = Column(Text)
    thumbnail = Column(Binary)

    children = relation('File',
                        backref=backref('parent', remote_side="File.id"),
                        order_by=[type, filename])
    tags = relation("Tag", secondary=tags_files, order_by="Tag.tag")
    #thumbnail = relation("Thumbnail", backref="file")
    images = relation("Image", backref="file")

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

    def generate_checksum(self):
        """
        Generate checksum of first 10MB of the file
        """
        if self.type != TYPE['file']:
            return

        buf = open(os.path.join(self.filepath, self.filename)).read(10485760)
        self.checksum = sha256(buf).hexdigest()

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
    group_id = Column(Integer, ForeignKey("groups.id"))
    tag = Column(Text)
    group = relation('Group', backref=backref('tags', remote_side="Group.id"))

    files = relation("File", secondary=tags_files)

    def __init__(self, tag=None, group=None):
        self.tag = tag
        self.group = group

    def __repr__(self):
        return "<Tag('%s', %s)>" % (str(self.tag), str(self.id))


#class Thumbnail(Base):
#    __tablename__ = "thumbnails"
#    id = Column(Integer, Sequence("thumbnail_id_seq"), primary_key=True)
#    file_id = Column(Integer, ForeignKey("files.id"))
#    filename = Column(Text)
#
#    def __init__(self, filename=None, file_obj=None):
#        self.filename = filename
#        self.file = file_obj
#        if self.filename:
#            self.save(self.filename)
#
#    def save(self, fname):
#        """
#        Create file related thumbnail, add it to the file object.
#        """
#        new_name = sha1(str(uuid1())).hexdigest()
#        new_name = [new_name[start:start+10] for start in range(0,
#                                                                len(new_name),
#                                                                10)]
#        try:
#            os.makedirs(os.path.join(IMG_PATH, *new_name[:-1]))
#        except OSError as exc:
#            if exc.errno != errno.EEXIST:
#                raise
#
#        ext = os.path.splitext(self.filename)[1]
#        if ext:
#            new_name.append("".join([new_name.pop(), ext]))
#
#        thumb = thumbnail.Thumbnail(self.filename)
#        thumb_tmp_name = thumb.save()
#        name, ext = os.path.splitext(new_name.pop())
#        new_name.append("".join([name, "_t", '.jpg']))
#        self.filename = os.path.sep.join(new_name)
#        shutil.move(thumb_tmp_name, os.path.join(IMG_PATH, *new_name))
#
#    def get_copy(self):
#        """
#        Create the very same object as self with exception of id field
#        """
#        thumb = Thumbnail()
#        thumb.filename = self.filename
#        return thumb
#
#    def __repr__(self):
#        return "<Thumbnail('%s', %s)>" % (str(self.filename), str(self.id))
#

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, Sequence("images_id_seq"), primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    image = Column(Binary)
    thumb = Column(Binary)
    checksum = Column(Text)

    def __init__(self, filename=None, file_obj=None):
        self.file = file_obj
        if filename:
            self.save(filename)

    def save(self, fname):
        """
        Save and create coressponding thumbnail (note: it differs from file
        related thumbnail!)
        """
        file_buffer = StringIO()

        with open(fname) as f:
            file_buffer.write(f.read())

        self.image = file_buffer.getvalue()
        self.checksum = sha256(file_buffer.getvalue()).hexdigest()

        file_buffer.seek(0)
        thumb = ThumbCreator(fname).generate()
        if thumb:
            self.thumb = thumb.getvalue()
            thumb.close()

        file_buffer.close()

    def get_copy(self):
        """
        Create the very same object as self with exception of id field
        """
        img = Image()
        img.image = self.image
        img.thumb = self.thumb
        img.checksum = self.checksum
        return img

    @property
    def fthumb(self):
        """
        Return file-like object with thumbnail
        """
        if self.thumb:
            buf = StringIO()
            buf.write(self.thumb)
            buf.seek(0)
            return buf
        else:
            return None

    @property
    def fimage(self):
        """
        Return file-like object with image
        """
        if self.image:
            buf = StringIO()
            buf.write(self.image)
            buf.seek(0)
            return buf
        else:
            return None

    def __repr__(self):
        return "<Image(%s)>" % str(self.id)


class Exif(Base):
    __tablename__ = "exif"
    id = Column(Integer, Sequence("exif_id_seq"), primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"))
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
    file_id = Column(Integer, ForeignKey("files.id"))
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
