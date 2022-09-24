"""
    Project: pyGTKtalog
    Description: Common database operations.
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-08-07
"""
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from pycatalog.logger import get_logger


# Prepare SQLAlchemy objects
Meta = MetaData()
Base = declarative_base(metadata=Meta)
Session = sessionmaker()
DbFilename = None

LOG = get_logger("dbcommon")


def connect(filename=None):
    """
    create engine and bind to Meta object.
    Arguments:
        @filename - string with absolute or relative path to sqlite database
                    file. If None, db in-memory will be created
    """
    global DbFilename

    if not filename:
        filename = ':memory:'

    LOG.info("db filename: %s" % filename)
    DbFilename = filename

    connect_string = "sqlite:///%s" % filename
    engine = create_engine(connect_string)
    Meta.bind = engine
    Meta.create_all(checkfirst=True)
    return engine
