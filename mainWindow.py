#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
GUI, main window class and correspondig methods for pyGTKtalog app.
"""
import sys
import os
import mimetypes
import popen2

import pygtk
import gtk
import gtk.glade
from config import Config

class PyGTKtalog:
    def __init__(self):
        
        self.conf = Config()
        
        self.gladefile = "glade/main.glade"
        self.pygtkcat = gtk.glade.XML(self.gladefile,"main")
        
        self.window = self.pygtkcat.get_widget("main")
        self.window.set_title("pyGTKtalog")
        icon = gtk.gdk.pixbuf_new_from_file("pixmaps/mainicon.png")
        self.window.set_icon_list(icon)
        
        self.progress = self.pygtkcat.get_widget("progressbar1")
        
        self.status = self.pygtkcat.get_widget("mainStatus")
        self.sbSearchCId = self.status.get_context_id('detailed res')
        self.sbid = self.status.push(self.sbSearchCId, "Idle")
        
        self.detailplaceholder = self.pygtkcat.get_widget("detailplace")
        self.detailplaceholder.set_sensitive(False)
        self.details = self.pygtkcat.get_widget("details")
        self.details.hide()
        
        self.widgets = ("discs","files","details",'save1','save_as1','cut1','copy1','paste1','delete1','add_cd','add_directory1')
        for w in self.widgets:
            a = self.pygtkcat.get_widget(w)
            a.set_sensitive(False)
        
        a = self.pygtkcat.get_widget('hpaned1')
        a.set_position(self.conf.confd['h'])
        a = self.pygtkcat.get_widget('vpaned1')
        a.set_position(self.conf.confd['v'])
        self.window.resize(self.conf.confd['wx'],self.conf.confd['wy'])
        
        # sygnały:
        dic = {"on_main_destroy_event"  :self.doQuit,
               "on_quit1_activate"      :self.doQuit,
               "on_new1_activate"       :self.newDB,
               "on_add_cd_activate"     :self.addCD,
        }
        
        # connect signals
        self.pygtkcat.signal_autoconnect(dic)
        self.window.connect("delete_event", self.deleteEvent)
    
    def storeSettings(self):
        """Store window size and pane position in config file (using config object)"""
        hpan = self.pygtkcat.get_widget('hpaned1')
        vpan = self.pygtkcat.get_widget('vpaned1')
        
        self.conf.confd['wx'], self.conf.confd['wy'] = self.window.get_size()
        self.conf.confd['h'],self.conf.confd['v'] = hpan.get_position(), vpan.get_position()
        
        self.conf.save()
        
        return
        
    def doQuit(self, widget):
        """quit and save window parameters to config file"""
        try:
            if widget.title:
                pass
        except:
            self.storeSettings()
        gtk.main_quit()
        return False
        
    def newDB(self,widget):
        """create database in temporary place"""
        self.window.set_title("untitled - pyGTKtalog")
        for w in self.widgets:
            try:
                a = self.pygtkcat.get_widget(w)
                a.set_sensitive(True)
                # PyGTK FAQ entry 23.20
            except:
                pass
            while gtk.events_pending():
                gtk.main_iteration()
                
        #self.details.set_sensitive(True)
        #self.details.destroy()
        
        #self.details = gtk.Button("Press mi or daj");
        #self.details.set_name("details")
        
        #self.detailplaceholder.add_with_viewport(self.details)
        #self.details.show()
        return
    
    def deleteEvent(self, widget, event, data=None):
        """checkout actual database changed. If so, do the necessary ask."""
        self.storeSettings()
        return False
   
    def run(self):
        self.window.show();
        gtk.main()
        
    def addCD(self,widget):
        self.scan(self.conf.confd['cd'])
        
    def scan(self,path):
        mime = mimetypes.MimeTypes()
        extensions = ('mkv','avi','ogg','mpg','wmv','mp4')
        
        count = 0
        for root,kat,plik in os.walk(path):
            for p in plik:
                count+=1
        
        frac = 1.0/count
        count = 1
        #self.progress.set_pulse_step(0)
        for root,kat,plik in os.walk(path):
            for p in plik:
                if p[-3:].lower() in extensions or \
                mime.guess_type(p)!= (None,None) and \
                mime.guess_type(p)[0].split("/")[0] == 'video':
                    # video only
                    # TODO: parametrize this loop!
                    info = popen2.popen4('midentify "' + os.path.join(root,p)+'"')[0].readlines()
                    video_format = ''
                    audio_codec = ''
                    video_codec = ''
                    video_x = ''
                    video_y = ''
                    for line in info:
                        l = line.split('=')
                        val = l[1].split('\n')[0]
                        if l[0] == 'ID_VIDEO_FORMAT':
                            video_format = val
                        elif l[0] == 'ID_AUDIO_CODEC':
                            audio_codec = val
                        elif l[0] == 'ID_VIDEO_CODEC':
                            video_codec = val
                        elif l[0] == 'ID_VIDEO_WIDTH':
                            video_x = val
                        elif l[0] == 'ID_VIDEO_HEIGHT':
                            video_y = val
                if self.sbid != 0:
                    """jeśli jest jakiś mesedż, usuń go"""
                    self.status.remove(self.sbSearchCId, self.sbid)
                self.sbid = self.status.push(self.sbSearchCId, "Scannig: %s" % (os.path.join(root,p)))
                
                self.progress.set_fraction(frac * count)
                count+=1
                
                # PyGTK FAQ entry 23.20
                while gtk.events_pending(): gtk.main_iteration()
        if self.sbid != 0:
            self.status.remove(self.sbSearchCId, self.sbid)
        self.sbid = self.status.push(self.sbSearchCId, "Idle")
        
        self.progress.set_fraction(0)

