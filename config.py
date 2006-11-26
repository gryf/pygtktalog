# This Python file uses the following encoding: utf-8
"""
config parser object
"""

#{{{ podstawowe importy i sprawdzenia
import sys
import os
from ConfigParser import ConfigParser

class Ini(object):
    def __init__(self):
        self.ini = []
        
    def add_section(self, section):
        self.ini.append("[%s]" % section)
        
    def add_key(self, key, value):
        self.ini.append("%s=%s" % (key, value))
        
    def add_comment(self, comment):
        self.ini.append(";%s" % comment)
        
    def add_verb(self, verb):
        self.ini.append(verb)

    def show(self):
        return "\n".join(self.ini)
        

class Config:
    ini = Ini()
    
    confd = {
        'wx' : 800,
        'wy' : 600,
        'h' : 200,
        'v' : 300,
        'exportxls' : False,
        'cd' : '/cdrom',
        'eject' : 'eject -r'
    }
    
    dictconf = {
        "main window width" : "wx",
        "main window height": "wy",
        "horizontal panes": "h",
        "vertical panes":"v",
        "export xls":"exportxls",
        "cd drive":"cd",
        "eject command":"eject",
    }
    
    dbool = ('exportxls')
    dstring = ('cd','eject')
    
    try:
        path = os.environ['HOME']
    except:
        path = "/tmp"
    
    def __init__(self):
        self.load()
        
    def save(self):
        try:
            os.lstat("%s/.pygtktalog" % self.path)
        except:
            print "Saving preferences to %s/.pygtktalog" % self.path
        newIni = Ini()
        newIni.add_section("pyGTKtalog conf")
        for opt in self.dictconf:
            newIni.add_key(opt,self.confd[self.dictconf[opt]])
        try:
            f = open("%s/.pygtktalog" % self.path,"w")
        except:
            print "Cannot open config file %s for writing." % (self.path, "/.pygtktalog") 
        f.write(newIni.show())
        f.close()
        
    def load(self):
        try:
            # try to read config file
            parser = ConfigParser()
            parser.read("%s/.pygtktalog" % self.path)
            for sec in parser.sections():
                if sec == 'pyGTKtalog conf':
                    for opt in parser.options(sec):
                        try:
                            if self.dictconf[opt] in self.dbool:
                                self.confd[self.dictconf[opt]] = parser.getboolean(sec,opt)
                            elif self.dictconf[opt] in self.dstring:
                                self.confd[self.dictconf[opt]] = parser.get(sec,opt)
                            else:
                                self.confd[self.dictconf[opt]] = parser.getint(sec,opt)
                        except:
                            pass
        except:
            pass

