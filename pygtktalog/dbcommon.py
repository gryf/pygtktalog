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

from pygtktalog.logger import get_logger


# setup SQLAlchemy logging facility
# TODO: Logger("sqlalchemy")
# or maybe it will be better to separate sqlalchemy stuff from application
#get_logger("sqlalchemy", 'INFO')

# Prepare SQLAlchemy objects
Meta = MetaData()
Base = declarative_base(metadata=Meta)
Session = sessionmaker()

LOG = get_logger("dbcommon")


def connect(filename=None):
    """
    create engine and bind to Meta object.
    Arguments:
        @filename - string with absolute or relative path to sqlite database
                    file. If None, db in-memory will be created
    """

    if not filename:
        filename = ':memory:'

    LOG.info("db filename: %s" % filename)

    connect_string = "sqlite:///%s" % filename
    engine = create_engine(connect_string)
    Meta.bind = engine
    Meta.create_all(checkfirst=True)
    return engine
