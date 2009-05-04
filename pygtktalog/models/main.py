"""
    Project: pyGTKtalog
    Description: Model for main application
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
from gtkmvc import Model

class MainModel(Model):
    status_bar_message = _("Idle")
    
    __observables__ = ("status_bar_message",)
