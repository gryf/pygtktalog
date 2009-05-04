"""
    Project: pyGTKtalog
    Description: Controller for main window
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-02
"""
from gtkmvc import Controller


class MainController(Controller):
    """
    Controller for main application window
    """

    def __init__(self, model, view):
        """Initialize main controller"""
        Controller.__init__(self, model, view)
    
    def register_view(self, view):
        """Default view registration stuff"""
        view['main'].show()

    def register_adapters(self):
        """
        progress bar/status bar adapters goes here
        """
        pass
