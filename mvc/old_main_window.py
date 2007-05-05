# This Python file uses the following encoding: utf-8
"""
GUI, main window class and correspondig methods for pyGTKtalog app.
"""
#{{{
licence = \
"""
GPL v2
http://www.gnu.org/licenses/gpl.txt
"""
#}}}

__version__ = "0.5"
import sys
import os
import mimetypes
import popen2
import datetime
import bz2

import pygtk
import gtk
import gtk.glade

from pysqlite2 import dbapi2 as sqlite
import mx.DateTime

from config import Config
import deviceHelper
import filetypeHelper
import dialogs
from preferences import Preferences
import db

class PyGTKtalog:
    def __init__(self):
        """ init"""
        # {{{ init
        self.conf = Config()
        self.conf.load()
        
        self.opened_catalog = None
        self.db_tmp_filename = None
        
        self.progress = self.pygtkcat.get_widget("progressbar1")
        
        # trees
        self.discs = self.pygtkcat.get_widget('discs')
        c = gtk.TreeViewColumn('Filename')
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        c.pack_start(cellpb, False)
        c.pack_start(cell, True)
        c.set_attributes(cellpb, stock_id=2)
        c.set_attributes(cell, text=1)
        
        self.discs.append_column(c)
        
        
        self.files = self.pygtkcat.get_widget('files')
        self.files.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        c = gtk.TreeViewColumn('Filename')
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        c.pack_start(cellpb, False)
        c.pack_start(cell, True)
        c.set_attributes(cellpb, stock_id=6)
        c.set_attributes(cell, text=1)
                
        c.set_sort_column_id(1)
        c.set_resizable(True)
        self.files.append_column(c)
        
        c = gtk.TreeViewColumn('Size',gtk.CellRendererText(), text=2)
        c.set_sort_column_id(2)
        c.set_resizable(True)
        self.files.append_column(c)
        
        c = gtk.TreeViewColumn('Date',gtk.CellRendererText(), text=3)
        c.set_sort_column_id(3)
        c.set_resizable(True)
        self.files.append_column(c)
        
        c = gtk.TreeViewColumn('Category',gtk.CellRendererText(), text=5)
        c.set_sort_column_id(5)
        c.set_resizable(True)
        self.files.append_column(c)
        
        
        # signals:
        dic = {"on_main_destroy_event"      :self.doQuit,
               "on_quit1_activate"          :self.doQuit,
               "on_tb_quit_clicked"         :self.doQuit,
               "on_new1_activate"           :self.newDB,
               "on_tb_new_clicked"          :self.newDB,
               "on_add_cd_activate"         :self.addCD,
               "on_tb_addcd_clicked"        :self.addCD,
               "on_add_directory1_activate" :self.addDirectory,
               "on_about1_activate"         :self.about,
               "on_properties1_activate"    :self.preferences,
               "on_status_bar1_activate"    :self.toggle_status_bar,
               "on_toolbar1_activate"       :self.toggle_toolbar,
               "on_save1_activate"          :self.save,
               "on_tb_save_clicked"         :self.save,
               "on_save_as1_activate"       :self.save_as,
               "on_tb_open_clicked"         :self.opendb,
               "on_open1_activate"          :self.opendb,
               "on_discs_cursor_changed"    :self.show_files,
               "on_discs_row_activated"     :self.collapse_expand_branch,
               "on_files_cursor_changed"    :self.show_details,
               "on_files_row_activated"     :self.change_view,
        }
        
        # connect signals
        self.pygtkcat.signal_autoconnect(dic)
        self.window.connect("delete_event", self.deleteEvent)
        #}}}
    
    def collapse_expand_branch(self, treeview, path, treecolumn):
        """if possible, expand or collapse branch of tree"""
        #{{{
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path,False)
        #}}}
        
    def show_details(self,treeview):
        """show details about file"""
        #{{{
        model, paths = treeview.get_selection().get_selected_rows()
        try:
            itera = model.get_iter(paths[0])
        except:
            if __debug__:
                print "[mainwin.py] insufficient iterator"
            return
            
        if model.get_value(itera,4) == 1:
            #directory, do nothin', just turn off view
            self.details.hide()
            buf = self.details.get_buffer()
            buf.set_text('')
            self.details.set_buffer(buf)
            if __debug__:
                print "[mainwin.py] directory selected"
        elif model.get_value(itera,4) > 1:
            #file, show what you got.
            self.details.show()
            txt = db.dbfile(self,self.con,self.cur).getInfo(model.get_value(itera,0))
            buf = self.details.get_buffer()
            buf.set_text(txt)
            self.details.set_buffer(buf)
            if __debug__:
                print "[mainwin.py] some other thing selected"
        #}}}
        
    def change_view(self, treeview, path, treecolumn):
        """change directory deep down"""
        #{{{
        model, paths = treeview.get_selection().get_selected_rows()
        itera = model.get_iter(paths[0])
        current_id = model.get_value(itera,0)
        if model.get_value(itera,4) == 1:
            self.filemodel = db.dbfile(self,self.con,self.cur).getCurrentFiles(current_id)
            self.files.set_model(self.filemodel)
            
            pat,col = self.discs.get_cursor()
            if pat!=None:
                if not self.discs.row_expanded(pat):
                    self.discs.expand_row(pat,False)
            #self.discs.unselect_all()
            
            model, paths = self.discs.get_selection().get_selected_rows()
            selected = None
            new_iter = self.discs.get_model().iter_children(model.get_iter(pat))
            if new_iter:
                while new_iter:
                    if model.get_value(new_iter,0) == current_id:
                        self.discs.set_cursor(model.get_path(new_iter))
                    new_iter = model.iter_next(new_iter)
            
            
        else:
            #directory, do nothin', just turn off view
            if __debug__:
                print "[mainwin.py] directory selected"
        #}}}
        
    def sort_files_view(self, model, iter1, iter2, data):
        print 'aaaa'
        
    def show_files(self,treeview):
        """show files after click on left side disc tree"""
        #{{{
        model = treeview.get_model()
        selected_item = model.get_value(model.get_iter(treeview.get_cursor()[0]),0)
        self.filemodel = db.dbfile(self,self.con,self.cur).getCurrentFiles(selected_item)
        self.files.set_model(self.filemodel)
                
        self.details.show()
        txt = db.dbfile(self,self.con,self.cur).getInfo(selected_item)
        buf = self.details.get_buffer()
        buf.set_text(txt)
        self.details.set_buffer(buf)
        if __debug__:
            print "[mainwin.py] some other thing selected"
        
        """
        iterator = treeview.get_model().get_iter_first();
        while iterator != None:
            if model.get_value(iterator,0) == selected:
                self.glade.get_widget(self.category_dict[model.get_value(iterator,0)]).show()
                self.desc.set_markup("<b>%s</b>" % selected)
            else:
                self.glade.get_widget(self.category_dict[model.get_value(iterator,0)]).hide()
            iterator = treeview.get_model().iter_next(iterator);
        """
        #}}}
        
    def opendb(self,widget):
        """open dtatabase file, decompress it to temp"""
        #{{{
        try:
            if self.unsaved_project:
                if self.conf.confd['confirmabandon']:
                    obj = dialogs.Qst('Unsaved data - pyGTKtalog','There is not saved database\nDo you really want to abandon it?')
                    if not obj.run():
                        return
        except AttributeError:
            pass
        
        
        #create filechooser dialog
        dialog = gtk.FileChooserDialog(
            title="Open catalog",
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK
            )
        )
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        f = gtk.FileFilter()
        f.set_name("Catalog files")
        f.add_pattern("*.pgt")
        dialog.add_filter(f)
        f = gtk.FileFilter()
        f.set_name("All files")
        f.add_pattern("*.*")
        dialog.add_filter(f)
        
        response = dialog.run()
        tmp = self.opened_catalog
        try:
            self.opened_catalog = dialog.get_filename()
        except:
            self.opened_catalog = tmp
            pass
        dialog.destroy()
        
        if response == gtk.RESPONSE_OK:
            # delete an existing temp file
            try:
                os.unlink(self.db_tmp_filename)
            except:
                pass
            
            # initial switches
            self.db_tmp_filename = None
            self.active_project = True
            self.unsaved_project = False
            self.window.set_title("untitled - pyGTKtalog")
        
            self.db_tmp_filename = "/tmp/pygtktalog%d.db" % datetime.datetime.now().microsecond
            
            source = bz2.BZ2File(self.opened_catalog, 'rb')
            destination = open(self.db_tmp_filename, 'wb')
            while True:
                try:
                    data = source.read(1024000)
                except:
                    dialogs.Err("Error opening file - pyGTKtalog","Cannot open file %s." % self.opened_catalog)
                    self.opened_catalog = None
                    self.newDB(self.window)
                    return
                if not data: break
                destination.write(data)
            destination.close()
            source.close()
            
            self.active_project = True
            self.unsaved_project = False
            
            self.con = sqlite.connect("%s" % self.db_tmp_filename, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
            self.cur = self.con.cursor()
            
            self.window.set_title("%s - pyGTKtalog" % self.opened_catalog)
            
            for w in self.widgets:
                try:
                    a = self.pygtkcat.get_widget(w)
                    a.set_sensitive(True)
                except:
                    pass
                # PyGTK FAQ entry 23.20
                while gtk.events_pending():
                    gtk.main_iteration()
            
            self.__display_main_tree()
        else:
            self.opened_catalog = tmp
            
        #}}}
        
    def __create_database(self,filename):
        """make all necessary tables in db file"""
        #{{{
        self.con = sqlite.connect("%s" % filename, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.cur = self.con.cursor()
        self.cur.execute("create table files(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, date datetime, size integer, type integer);")
        self.cur.execute("create table files_connect(id INTEGER PRIMARY KEY AUTOINCREMENT, parent numeric, child numeric, depth numeric);")
        self.cur.execute("insert into files values(1, 'root', 0, 0, 0);")
        self.cur.execute("insert into files_connect values(1, 1, 1, 0);")
        #}}}
            
    def save(self,widget):
        """save database to file. compress it with gzip"""
        #{{{
        if self.opened_catalog == None:
            self.save_as(widget)
        else:
            self.__compress_and_save(self.opened_catalog)
        #}}}
        
    def save_as(self,widget):
        """save database to another file. compress it with gzip"""
        #{{{
        dialog = gtk.FileChooserDialog(
            title="Save catalog as...",
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE,
                gtk.RESPONSE_OK
            )
        )
        
        dialog.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_do_overwrite_confirmation(True)
        if widget.get_name() == 'save1':
            dialog.set_title('Save catalog to file...')
        
        f = gtk.FileFilter()
        f.set_name("Catalog files")
        f.add_pattern("*.pgt")
        dialog.add_filter(f)
        f = gtk.FileFilter()
        f.set_name("All files")
        f.add_pattern("*.*")
        dialog.add_filter(f)
        
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            if filename[-4] == '.':
                if filename[-3:].lower() != 'pgt':
                    filename = filename + '.pgt'
                else:
                    filename = filename[:-3] + 'pgt'
            else:
                filename = filename + '.pgt'
            self.__compress_and_save(filename)
            self.opened_catalog = filename
            
        dialog.destroy()
        #}}}
        
    def __compress_and_save(self,filename):
        """compress and save temporary file to catalog"""
        #{{{
        source = open(self.db_tmp_filename, 'rb')
        destination = bz2.BZ2File(filename, 'w')
            
        while True:
            data = source.read(1024000)
            if not data: break
            destination.write(data)
            
        destination.close()
        source.close()
        self.window.set_title("%s - pyGTKtalog" % filename)
        self.unsaved_project = False
        #}}}
        
    def toggle_toolbar(self,widget):
        """toggle visibility of toolbar bar"""
        #{{{
        self.conf.confd['showtoolbar'] = self.menu_toolbar.get_active()
        if self.menu_toolbar.get_active():
            self.toolbar.show()
        else:
            self.toolbar.hide()
        #}}}
    
    def toggle_status_bar(self,widget):
        """toggle visibility of statusbat and progress bar"""
        #{{{
        self.conf.confd['showstatusbar'] = self.menu_statusbar.get_active()
        if self.menu_statusbar.get_active():
            self.statusprogress.show()
        else:
            self.statusprogress.hide()
        #}}}
    
    
        
    def preferences(self,widget):
        """display preferences window"""
        #{{{
        a = Preferences()
        #}}}
    
    def doQuit(self, widget):
        """quit and save window parameters to config file"""
        #{{{
        try:
            if widget.title:
                pass
        except:
            # check if any unsaved project is on go.
            try:
                if self.unsaved_project:
                    if self.conf.confd['confirmquit']:
                        obj = dialogs.Qst('Quit application - pyGTKtalog','There is not saved database\nDo you really want to quit?')
                        if not obj.run():
                            return
            except AttributeError:
                pass
            self.storeSettings()
        gtk.main_quit()
        try:
            self.con.commit()
            self.cur.close()
            self.con.close()
        except:
            pass
        try:
            os.unlink(self.db_tmp_filename)
        except:
            pass
        return False
        #}}}
        
    def newDB(self,widget):
        """create database in temporary place"""
        #{{{
        try:
            if self.unsaved_project:
                if self.conf.confd['confirmabandon']:
                    obj = dialogs.Qst('Unsaved data - pyGTKtalog','There is not saved database\nDo you really want to abandon it?')
                    if not obj.run():
                        return
        except AttributeError:
            pass
        self.active_project = True
        self.unsaved_project = False
        
        self.window.set_title("untitled - pyGTKtalog")
        for w in self.widgets:
            try:
                a = self.pygtkcat.get_widget(w)
                a.set_sensitive(True)
            except:
                pass
            # PyGTK FAQ entry 23.20
            while gtk.events_pending():
                gtk.main_iteration()
                
        # Create new database
        if self.db_tmp_filename!=None:
            self.con.commit()
            self.cur.close()
            self.con.close()
            os.unlink(self.db_tmp_filename)
            
        self.db_tmp_filename = datetime.datetime.now()
        self.db_tmp_filename = "/tmp/pygtktalog%d.db" % self.db_tmp_filename.microsecond
        self.__create_database(self.db_tmp_filename)
        
        #clear treeview, if possible
        try:
            self.discs.get_model().clear()
        except:
            pass
        try:
            self.files.get_model().clear()
        except:
            pass
        
        #}}}
    
    def deleteEvent(self, widget, event, data=None):
        """checkout actual database changed. If so, do the necessary ask."""
        #{{{
        try:
            if self.unsaved_project:
                if self.conf.confd['confirmquit']:
                    obj = dialogs.Qst('Quit application - pyGTKtalog','There is not saved database\nDo you really want to quit?')
                    if not obj.run():
                        return True
        except AttributeError:
            pass
        self.storeSettings()
        try:
            self.cur.close()
        except:
            pass
        try:
            self.con.close()
        except:
            pass
        try:
            os.unlink(self.db_tmp_filename)
        except:
            pass
        return False
        #}}}
    
    def run(self):
        """show window and run app"""
        #{{{
        self.window.show();
        gtk.main()
        #}}}
        
    def addDirectory(self,widget):
        """add directory structure from given location"""
        #{{{
        obj = dialogs.PointDirectoryToAdd()
        res = obj.run()
        if res !=(None,None):
            self.__scan(res[1],res[0])
        #}}}
        
    def addCD(self,widget):
        """add directory structure from cd/dvd disc"""
        #{{{
        mount = deviceHelper.volmount(self.conf.confd['cd'])
        if mount == 'ok':
            guessed_label = deviceHelper.volname(self.conf.confd['cd'])
            obj = dialogs.InputDiskLabel(guessed_label)
            label = obj.run()
            if label != None:
                
                self.__scan(self.conf.confd['cd'],label)
                
                # umount/eject cd
                if self.conf.confd['eject']:
                    msg = deviceHelper.eject_cd()
                    if msg != 'ok':
                        dialogs.Wrn("error ejecting device - pyGTKtalog","Cannot eject device pointed to %s.\nLast eject message:\n<tt>%s</tt>" % (self.conf.confd['cd'],msg))
                else:
                    msg = deviceHelper.volumount(self.conf.confd['cd'])
                    if msg != 'ok':
                        dialogs.Wrn("error unmounting device - pyGTKtalog","Cannot unmount device pointed to %s.\nLast umount message:\n<tt>%s</tt>" % (self.conf.confd['cd'],msg))
        else:
            dialogs.Wrn("error mounting device - pyGTKtalog","Cannot mount device pointed to %s.\nLast mount message:\n<tt>%s</tt>" % (self.conf.confd['cd'],mount))
        #}}}
    
    def __scan(self,path,label,currentdb=None):
        """scan content of the given path"""
        #{{{
        mime = mimetypes.MimeTypes()
        mov_ext = ('mkv','avi','ogg','mpg','wmv','mp4','mpeg')
        img_ext = ('jpg','jpeg','png','gif','bmp','tga','tif','tiff','ilbm','iff','pcx')
        
        # count files in directory tree
        count = 0
        if self.StatusbarID != 0:
            self.status.remove(self.ContextID, self.StatusbarID)
        self.StatusbarID = self.status.push(self.ContextID, "Calculating number of files in directory tree...")
        for root,kat,plik in os.walk(path):
            for p in plik:
                count+=1
                while gtk.events_pending(): gtk.main_iteration()
        frac = 1.0/count
        
        self.count = 0
        
        def __recurse(path,name,wobj,date=0,frac=0,size=0,idWhere=1):
            """recursive scans the path
            path = path string
            name = field name
            wobj = obiekt katalogu
            date = data pliku
            frac - kolejne krok w statusbarze.
            idWhere - simple id parent, or "place" where to add node
            """
            #{{{
            _size = size
            walker = os.walk(path)
            root,dirs,files = walker.next()
            ftype = 1
            self.cur.execute("insert into files(filename, date, size, type) values(?,?,?,?)",(name, date, 0, ftype))
            self.cur.execute("select seq FROM sqlite_sequence WHERE name='files'")
            currentid=self.cur.fetchone()[0]
            self.cur.execute("insert into files_connect(parent,child,depth) values(?,?,?)",(currentid, currentid, 0))
            
            if idWhere>0:
                self.cur.execute("insert into files_connect(parent, child, depth) select r1.parent, r2.child, r1.depth + r2.depth + 1 as depth FROM files_connect r1, files_connect r2 WHERE r1.child = ? AND r2.parent = ? ",(idWhere, currentid))
            
            for i in dirs:
                st = os.stat(os.path.join(root,i))
                _size = _size + __recurse(os.path.join(path,i),i,wobj,st.st_mtime,frac,0,currentid)
            
            for i in files:
                self.count = self.count + 1
                st = os.stat(os.path.join(root,i))
                
                ### scan files
                if i[-3:].lower() in mov_ext or \
                mime.guess_type(i)!= (None,None) and \
                mime.guess_type(i)[0].split("/")[0] == 'video':
                    # video only
                    info = filetypeHelper.guess_video(os.path.join(root,i))
                elif i[-3:].lower() in img_ext or \
                mime.guess_type(i)!= (None,None) and \
                mime.guess_type(i)[0].split("/")[0] == 'image':
                    pass
                ### end of scan
                
                # progress/status
                if wobj.StatusbarID != 0:
                    wobj.status.remove(wobj.ContextID, wobj.StatusbarID)
                wobj.StatusbarID = wobj.status.push(wobj.ContextID, "Scannig: %s" % (os.path.join(root,i)))
                wobj.progress.set_fraction(frac * self.count)
                # PyGTK FAQ entry 23.20
                while gtk.events_pending(): gtk.main_iteration()
                
                _size = _size + st.st_size
                
                self.cur.execute('insert into files(filename, date, size, type) values(?,?,?,?)',(i, st.st_mtime, st.st_size,2))
                self.cur.execute("select seq FROM sqlite_sequence WHERE name='files'")
                currentfileid=self.cur.fetchone()[0]
                self.cur.execute("insert into files_connect(parent,child,depth) values(?,?,?)",(currentfileid, currentfileid, 0))
                if currentid>0:
                    self.cur.execute("insert into files_connect(parent, child, depth) select r1.parent, r2.child, r1.depth + r2.depth + 1 as depth FROM files_connect r1, files_connect r2 WHERE r1.child = ? AND r2.parent = ? ",(currentid, currentfileid))
                self.con.commit()
            
            self.cur.execute("update files set size=? where id=?",(_size, currentid))
            return _size
            #}}}
        
        self.con.commit()
        __recurse(path,label,self,0,frac)
        self.unsaved_project = True
        self.__display_main_tree()
        
        if self.StatusbarID != 0:
            self.status.remove(self.ContextID, self.StatusbarID)
        self.StatusbarID = self.status.push(self.ContextID, "Idle")
        
        self.progress.set_fraction(0)
        #}}}
        
    def __display_main_tree(self):
        """refresh tree with model form db"""
        #{{{
        try:
            self.dirmodel = db.dbfile(self,self.con,self.cur).getDirectories()
        except:
            dialogs.Err("Error opening file - pyGTKtalog","Cannot open file %s." % self.opened_catalog)
            self.newDB(self.window)
            return
        #self.dirmodel.set_sort_column_id(1,gtk.SORT_ASCENDING)
        self.discs.set_model(self.dirmodel)
        #}}}
        
    def about(self,widget):
        """simple about dialog"""
        #{{{
        dialogs.Abt("pyGTKtalog", __version__, "About", ["Roman 'gryf' Dobosz"], licence)
        #}}}

