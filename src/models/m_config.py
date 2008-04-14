# This Python file uses the following encoding: utf-8
#
#  Author: Roman 'gryf' Dobosz  gryf@elysium.pl
#
#  Copyright (C) 2007 by Roman 'gryf' Dobosz
#
#  This file is part of pyGTKtalog.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

#  -------------------------------------------------------------------------

from gtkmvc import Model

import sys
import os

import gtk
import gobject

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

class ConfigModel(Model):
    ini = Ini()
    
    __properties__ = {}
    
    filetype_list = ['Images', 'Movies']
    
    confd = {
        'savewin': True,
        'savepan': True,
        'wx': 800,
        'wy': 600,
        'h': 200,
        'v': 300,
        'eject': True,
        'compress': True,
        
        'exportxls': False,
        
        'confirmquit': True,
        'confirmabandon': True,
        'mntwarn': True,
        'delwarn': True,
        
        'cd': '/mnt/cdrom',
        'ejectapp': 'eject -r',
        
        'imgview': False,
        'imgprog': 'gqview',
        
        'retrive': False,
        
        'thumbs': True,
        'exif': True,
        'gthumb': False,
        
        'extensions': {'bmp':'identify %s',
            'gif':'identify "%s"',
            'jpg':'identify "%s"',
            'jpeg':'identify "%s"',
            'png':'identify "%s"',
            'avi':'midentify "%s"',
            'mkv':'midentify "%s"',
            'mpg':'midentify "%s"',
            'mpeg':'midentify "%s"',
            'wmv':'midentify "%s"',
        },
        
        'showtoolbar':True,
        'showstatusbar':True,
    }
    
    dictconf = {
        "save main window size" : "savewin",
        "save panes size" : "savepan",
        "main window width" : "wx",
        "main window height": "wy",
        "horizontal panes": "h",
        "vertical panes":"v",
        "export xls":"exportxls",
        "cd drive":"cd",
        "eject command":"ejectapp",
        "eject":"eject",
        "image support":"thumbs",
        'confirm quit':'confirmquit',
        'warn mount/umount errors':'mntwarn',
        'warn on delete':'delwarn',
        'confirm abandon current catalog':'confirmabandon',
        'show toolbar':'showtoolbar',
        'show statusbar and progress bar':'showstatusbar',
        'compress catalog':'compress',
        'retrive extra informatin':'retrive',
        'scan exif data':'exif',
        'include gthumb image description':'gthumb',
        'use external image viewer':'imgview',
        'external image viewer program':'imgprog',
    }
    
    dbool = (
             'exportxls',
             'thumbs',
             'savewin',
             'savepan',
             'eject',
             'gthumb',
             'exif',
             'confirmquit',
             'mntwarn',
             'delwarn',
             'confirmabandon',
             'showtoolbar',
             'showstatusbar',
             'delwarn',
             'compress',
             'retrive',
             'imgview',
    )
    
    recent = []
    RECENT_MAX = 10
    
    dstring = ('cd','ejectapp','imgprog')
    
    try:
        path = os.environ['HOME']
    except:
        path = "/tmp"
    
    def __init__(self):
        Model.__init__(self)
        self.category_tree = gtk.ListStore(gobject.TYPE_STRING)
        
        self.refresh_ext()
        return
    
        
    def refresh_ext(self):
        self.ext_tree = gtk.ListStore(gobject.TYPE_STRING,
                                      gobject.TYPE_STRING)
        keys = sorted(self.confd['extensions'].keys())
        for i in keys:
            myiter = self.ext_tree.insert_before(None,None)
            self.ext_tree.set_value(myiter, 0, i)
            self.ext_tree.set_value(myiter, 1, self.confd['extensions'][i])
        
    def save(self):
        try:
            os.lstat("%s/.pygtktalog" % self.path)
        except:
            print "Saving preferences to %s/.pygtktalog" % self.path
            if __debug__:
                print "m_config.py: save() Saving preferences to %s/.pygtktalog" % self.path
        newIni = Ini()
        
        # main section
        newIni.add_section("pyGTKtalog conf")
        for opt in self.dictconf:
            newIni.add_key(opt,self.confd[self.dictconf[opt]])
            
        # recent section
        newIni.add_section("pyGTKtalog recent")
        
        count = 1
        max_count = self.RECENT_MAX + 1
        for opt in self.recent:
            if count < max_count:
                newIni.add_key(count, opt)
            else:
                break
            count+=1
        
        # extensions sections
        newIni.add_section("extensions")
        count = 1
        for i in self.confd['extensions']:
            newIni.add_key(i, self.confd['extensions'][i])
            count+=1
            
        # write config
        try:
            f = open("%s/.pygtktalog" % self.path,"w")
            success = True
        except:
            if __debug__:
                print "m_config.py: save() Cannot open config file %s for writing." % (self.path, "/.pygtktalog")
            success = False
        f.write(newIni.show())
        f.close()
        return success
        
    def load(self):
        try:
        # try to read config file
            parser = ConfigParser()
            parser.read("%s/.pygtktalog" % self.path)
            r = {}
            self.recent = []
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
                            if __debug__:
                                print "m_config.py: load() failed to parse option:", opt
                            pass
                elif sec == 'pyGTKtalog recent':
                    for opt in parser.options(sec):
                        try:
                            r[int(opt)] = parser.get(sec,opt)
                        except:
                            if __debug__:
                                print "m_config.py: load() failed to parse option:", opt
                            pass
                elif sec == 'extensions':
                    self.confd['extensions'] = {}
                    for opt in parser.options(sec):
                        try:
                            self.confd['extensions'][opt] = parser.get(sec, opt)
                        except:
                            if __debug__:
                                print "m_config.py: load() failed to parse option:", opt
                            pass
                
            for i in range(1, self.RECENT_MAX + 1):
                if r.has_key(i):
                    self.recent.append(r[i])
                
        except:
            if __debug__:
                print "m_config.py: load() load config file failed"
            pass

    def add_recent(self, path):
        if not path:
            return
            
        if  path in self.recent:
            self.recent.remove(path)
            self.recent.insert(0,path)
            return
            
        self.recent.insert(0,path)
        if len(self.recent) > self.RECENT_MAX:
            self.recent = self.recent[:self.RECENT_MAX]
        return
        
    def __str__(self):
        """show prefs in string way"""
        string = "[varname]\tvalue\n"
        for i in self.confd:
            string+="%s\t%s\n" % (i,self.confd[i])
        return string
