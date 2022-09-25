"""
    Project: pyGTKtalog
    Description: Definition of DB objects classes. Using SQLAlchemy.
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-07
"""
import os
import shutil

from sqlalchemy import Column, Table, Integer, Text
from sqlalchemy import DateTime, ForeignKey, Sequence
from sqlalchemy.orm import relation, backref

from pycatalog.dbcommon import Base
from pycatalog.logger import get_logger


LOG = get_logger()

tags_files = Table("tags_files", Base.metadata,
                   Column("file_id", Integer, ForeignKey("files.id")),
                   Column("tag_id", Integer, ForeignKey("tags.id")))

TYPE = {'root': 0, 'dir': 1, 'file': 2, 'link': 3}


class File(Base):
    """
    File mapping. Instances of this object can reference other File object
    which make the structure to be tree-like
    """
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
        return "<File('%s', %s)>" % (self.filename, str(self.id))

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
    """TODO: what is this class for?"""
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
    """Tag mapping"""
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


class Exif(Base):
    """Selected EXIF information"""
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
    """Gthumb information"""
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


class Config(Base):
    """Per-database configuration"""
    __tablename__ = "config"
    id = Column(Integer, Sequence("config_id_seq"), primary_key=True)
    key = Column(Text)
    value = Column(Text)

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def __repr__(self):
        return "<Config('%s', '%s')>" % (str(self.key), str(self.value))
