# This Python file uses the following encoding: utf-8

import utils._importer
import utils.globals
from gtkmvc import View
import os.path

class ConfigView(View):
    """Preferences window from glade file """
    GLADE = os.path.join(utils.globals.GLADE_DIR, "config.glade")
    def __init__(self, ctrl):
        View.__init__(self, ctrl, self.GLADE)
        return
    pass # end of class
