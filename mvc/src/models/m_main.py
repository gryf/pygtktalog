# This Python file uses the following encoding: utf-8

import utils._importer
import utils.globals
from gtkmvc import Model

from models.m_config import ConfigModel

class MainModel(Model):
    """Our model contains a numeric counter and a numeric value that
    holds the value that the counter must be assigned to when we the
    model is reset"""
    
    __properties__ = {}
    
    def __init__(self):
        Model.__init__(self)
        self.config = ConfigModel()
        self.config.load()
        return
        
    pass # end of class
