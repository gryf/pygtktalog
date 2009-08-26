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


# Prepare SQLAlchemy objects
Meta = MetaData()
Base = declarative_base(metadata=Meta)
Session = sessionmaker()

def connect(filename):
    """
    create engine and bind to Meta object.
    Arguments:
        @filename - string with absolute or relative path to sqlite database
                    file.
    """

    engine = create_engine("sqlite:///%s" % filename, echo=True)
    Meta.bind = engine
    Meta.create_all()
