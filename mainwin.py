# This Python file uses the following encoding: utf-8
"""
GUI, main window class and correspondig methods for pyGTKtalog app.
"""
#{{{
licence = \
"""
		    GNU GENERAL PUBLIC LICENSE
		       Version 2, June 1991

 Copyright (C) 1989, 1991 Free Software Foundation, Inc.
                       51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

			    Preamble

  The licenses for most software are designed to take away your
freedom to share and change it.  By contrast, the GNU General Public
License is intended to guarantee your freedom to share and change free
software--to make sure the software is free for all its users.  This
General Public License applies to most of the Free Software
Foundation's software and to any other program whose authors commit to
using it.  (Some other Free Software Foundation software is covered by
the GNU Library General Public License instead.)  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
this service if you wish), that you receive source code or can get it
if you want it, that you can change the software or use pieces of it
in new free programs; and that you know you can do these things.

  To protect your rights, we need to make restrictions that forbid
anyone to deny you these rights or to ask you to surrender the rights.
These restrictions translate to certain responsibilities for you if you
distribute copies of the software, or if you modify it.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must give the recipients all the rights that
you have.  You must make sure that they, too, receive or can get the
source code.  And you must show them these terms so they know their
rights.

  We protect your rights with two steps: (1) copyright the software, and
(2) offer you this license which gives you legal permission to copy,
distribute and/or modify the software.

  Also, for each author's protection and ours, we want to make certain
that everyone understands that there is no warranty for this free
software.  If the software is modified by someone else and passed on, we
want its recipients to know that what they have is not the original, so
that any problems introduced by others will not reflect on the original
authors' reputations.

  Finally, any free program is threatened constantly by software
patents.  We wish to avoid the danger that redistributors of a free
program will individually obtain patent licenses, in effect making the
program proprietary.  To prevent this, we have made it clear that any
patent must be licensed for everyone's free use or not licensed at all.

  The precise terms and conditions for copying, distribution and
modification follow.

		    GNU GENERAL PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. This License applies to any program or other work which contains
a notice placed by the copyright holder saying it may be distributed
under the terms of this General Public License.  The "Program", below,
refers to any such program or work, and a "work based on the Program"
means either the Program or any derivative work under copyright law:
that is to say, a work containing the Program or a portion of it,
either verbatim or with modifications and/or translated into another
language.  (Hereinafter, translation is included without limitation in
the term "modification".)  Each licensee is addressed as "you".

Activities other than copying, distribution and modification are not
covered by this License; they are outside its scope.  The act of
running the Program is not restricted, and the output from the Program
is covered only if its contents constitute a work based on the
Program (independent of having been made by running the Program).
Whether that is true depends on what the Program does.

  1. You may copy and distribute verbatim copies of the Program's
source code as you receive it, in any medium, provided that you
conspicuously and appropriately publish on each copy an appropriate
copyright notice and disclaimer of warranty; keep intact all the
notices that refer to this License and to the absence of any warranty;
and give any other recipients of the Program a copy of this License
along with the Program.

You may charge a fee for the physical act of transferring a copy, and
you may at your option offer warranty protection in exchange for a fee.

  2. You may modify your copy or copies of the Program or any portion
of it, thus forming a work based on the Program, and copy and
distribute such modifications or work under the terms of Section 1
above, provided that you also meet all of these conditions:

    a) You must cause the modified files to carry prominent notices
    stating that you changed the files and the date of any change.

    b) You must cause any work that you distribute or publish, that in
    whole or in part contains or is derived from the Program or any
    part thereof, to be licensed as a whole at no charge to all third
    parties under the terms of this License.

    c) If the modified program normally reads commands interactively
    when run, you must cause it, when started running for such
    interactive use in the most ordinary way, to print or display an
    announcement including an appropriate copyright notice and a
    notice that there is no warranty (or else, saying that you provide
    a warranty) and that users may redistribute the program under
    these conditions, and telling the user how to view a copy of this
    License.  (Exception: if the Program itself is interactive but
    does not normally print such an announcement, your work based on
    the Program is not required to print an announcement.)

These requirements apply to the modified work as a whole.  If
identifiable sections of that work are not derived from the Program,
and can be reasonably considered independent and separate works in
themselves, then this License, and its terms, do not apply to those
sections when you distribute them as separate works.  But when you
distribute the same sections as part of a whole which is a work based
on the Program, the distribution of the whole must be on the terms of
this License, whose permissions for other licensees extend to the
entire whole, and thus to each and every part regardless of who wrote it.

Thus, it is not the intent of this section to claim rights or contest
your rights to work written entirely by you; rather, the intent is to
exercise the right to control the distribution of derivative or
collective works based on the Program.

In addition, mere aggregation of another work not based on the Program
with the Program (or with a work based on the Program) on a volume of
a storage or distribution medium does not bring the other work under
the scope of this License.

  3. You may copy and distribute the Program (or a work based on it,
under Section 2) in object code or executable form under the terms of
Sections 1 and 2 above provided that you also do one of the following:

    a) Accompany it with the complete corresponding machine-readable
    source code, which must be distributed under the terms of Sections
    1 and 2 above on a medium customarily used for software interchange; or,

    b) Accompany it with a written offer, valid for at least three
    years, to give any third party, for a charge no more than your
    cost of physically performing source distribution, a complete
    machine-readable copy of the corresponding source code, to be
    distributed under the terms of Sections 1 and 2 above on a medium
    customarily used for software interchange; or,

    c) Accompany it with the information you received as to the offer
    to distribute corresponding source code.  (This alternative is
    allowed only for noncommercial distribution and only if you
    received the program in object code or executable form with such
    an offer, in accord with Subsection b above.)

The source code for a work means the preferred form of the work for
making modifications to it.  For an executable work, complete source
code means all the source code for all modules it contains, plus any
associated interface definition files, plus the scripts used to
control compilation and installation of the executable.  However, as a
special exception, the source code distributed need not include
anything that is normally distributed (in either source or binary
form) with the major components (compiler, kernel, and so on) of the
operating system on which the executable runs, unless that component
itself accompanies the executable.

If distribution of executable or object code is made by offering
access to copy from a designated place, then offering equivalent
access to copy the source code from the same place counts as
distribution of the source code, even though third parties are not
compelled to copy the source along with the object code.

  4. You may not copy, modify, sublicense, or distribute the Program
except as expressly provided under this License.  Any attempt
otherwise to copy, modify, sublicense or distribute the Program is
void, and will automatically terminate your rights under this License.
However, parties who have received copies, or rights, from you under
this License will not have their licenses terminated so long as such
parties remain in full compliance.

  5. You are not required to accept this License, since you have not
signed it.  However, nothing else grants you permission to modify or
distribute the Program or its derivative works.  These actions are
prohibited by law if you do not accept this License.  Therefore, by
modifying or distributing the Program (or any work based on the
Program), you indicate your acceptance of this License to do so, and
all its terms and conditions for copying, distributing or modifying
the Program or works based on it.

  6. Each time you redistribute the Program (or any work based on the
Program), the recipient automatically receives a license from the
original licensor to copy, distribute or modify the Program subject to
these terms and conditions.  You may not impose any further
restrictions on the recipients' exercise of the rights granted herein.
You are not responsible for enforcing compliance by third parties to
this License.

  7. If, as a consequence of a court judgment or allegation of patent
infringement or for any other reason (not limited to patent issues),
conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot
distribute so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you
may not distribute the Program at all.  For example, if a patent
license would not permit royalty-free redistribution of the Program by
all those who receive copies directly or indirectly through you, then
the only way you could satisfy both it and this License would be to
refrain entirely from distribution of the Program.

If any portion of this section is held invalid or unenforceable under
any particular circumstance, the balance of the section is intended to
apply and the section as a whole is intended to apply in other
circumstances.

It is not the purpose of this section to induce you to infringe any
patents or other property right claims or to contest validity of any
such claims; this section has the sole purpose of protecting the
integrity of the free software distribution system, which is
implemented by public license practices.  Many people have made
generous contributions to the wide range of software distributed
through that system in reliance on consistent application of that
system; it is up to the author/donor to decide if he or she is willing
to distribute software through any other system and a licensee cannot
impose that choice.

This section is intended to make thoroughly clear what is believed to
be a consequence of the rest of this License.

  8. If the distribution and/or use of the Program is restricted in
certain countries either by patents or by copyrighted interfaces, the
original copyright holder who places the Program under this License
may add an explicit geographical distribution limitation excluding
those countries, so that distribution is permitted only in or among
countries not thus excluded.  In such case, this License incorporates
the limitation as if written in the body of this License.

  9. The Free Software Foundation may publish revised and/or new versions
of the General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

Each version is given a distinguishing version number.  If the Program
specifies a version number of this License which applies to it and "any
later version", you have the option of following the terms and conditions
either of that version or of any later version published by the Free
Software Foundation.  If the Program does not specify a version number of
this License, you may choose any version ever published by the Free Software
Foundation.

  10. If you wish to incorporate parts of the Program into other free
programs whose distribution conditions are different, write to the author
to ask for permission.  For software which is copyrighted by the Free
Software Foundation, write to the Free Software Foundation; we sometimes
make exceptions for this.  Our decision will be guided by the two goals
of preserving the free status of all derivatives of our free software and
of promoting the sharing and reuse of software generally.

			    NO WARRANTY

  11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
REPAIR OR CORRECTION.

  12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
POSSIBILITY OF SUCH DAMAGES.

		     END OF TERMS AND CONDITIONS

	    How to Apply These Terms to Your New Programs

  If you develop a new program, and you want it to be of the greatest
possible use to the public, the best way to achieve this is to make it
free software which everyone can redistribute and change under these terms.

  To do so, attach the following notices to the program.  It is safest
to attach them to the start of each source file to most effectively
convey the exclusion of warranty; and each file should have at least
the "copyright" line and a pointer to where the full notice is found.

    <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) <year>  <name of author>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


Also add information on how to contact you by electronic and paper mail.

If the program is interactive, make it output a short notice like this
when it starts in an interactive mode:

    Gnomovision version 69, Copyright (C) year name of author
    Gnomovision comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details.

The hypothetical commands `show w' and `show c' should show the appropriate
parts of the General Public License.  Of course, the commands you use may
be called something other than `show w' and `show c'; they could even be
mouse-clicks or menu items--whatever suits your program.

You should also get your employer (if you work as a programmer) or your
school, if any, to sign a "copyright disclaimer" for the program, if
necessary.  Here is a sample; alter the names:

  Yoyodyne, Inc., hereby disclaims all copyright interest in the program
  `Gnomovision' (which makes passes at compilers) written by James Hacker.

  <signature of Ty Coon>, 1 April 1989
  Ty Coon, President of Vice

This General Public License does not permit incorporating your program into
proprietary programs.  If your program is a subroutine library, you may
consider it more useful to permit linking proprietary applications with the
library.  If this is what you want to do, use the GNU Library General
Public License instead of this License.
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
        
        self.widgets = ("discs","files","details",'save1','save_as1',
                        'cut1','copy1','paste1','delete1','add_cd','add_directory1',
                        'tb_save','tb_addcd','tb_find'
                        )
        
        for w in self.widgets:
            a = self.pygtkcat.get_widget(w)
            a.set_sensitive(False)
        
        # toolbar/status bar
        self.menu_toolbar = self.pygtkcat.get_widget("toolbar1")
        self.menu_toolbar.set_active(self.conf.confd['showtoolbar'])
        self.menu_statusbar = self.pygtkcat.get_widget("status_bar1")
        self.menu_statusbar.set_active(self.conf.confd['showstatusbar'])
        self.toolbar = self.pygtkcat.get_widget("maintoolbar")
        if self.conf.confd['showtoolbar']:
            self.toolbar.show()
        else:
            self.toolbar.hide()
        self.statusprogress = self.pygtkcat.get_widget("statusprogress")
        if self.conf.confd['showstatusbar']:
            self.statusprogress.show()
        else:
            self.statusprogress.hide()
        
        # trees
        self.discs = self.pygtkcat.get_widget('discs')
        self.discs.append_column(gtk.TreeViewColumn('filename',gtk.CellRendererText(), text=1))
        
        self.files = self.pygtkcat.get_widget('files')
        
        c = gtk.TreeViewColumn('Filename',gtk.CellRendererText(), text=1)
        c.set_sort_column_id(1)
        self.files.append_column(c)
        
        c = gtk.TreeViewColumn('Size',gtk.CellRendererText(), text=2)
        c.set_sort_column_id(2)
        self.files.append_column(c)
        
        c = gtk.TreeViewColumn('Date',gtk.CellRendererText(), text=3)
        c.set_sort_column_id(3)
        self.files.append_column(c)
        
        c = gtk.TreeViewColumn('Category',gtk.CellRendererText(), text=5)
        c.set_sort_column_id(5)
        self.files.append_column(c)
        
        # window size
        a = self.pygtkcat.get_widget('hpaned1')
        a.set_position(self.conf.confd['h'])
        a = self.pygtkcat.get_widget('vpaned1')
        a.set_position(self.conf.confd['v'])
        self.window.resize(self.conf.confd['wx'],self.conf.confd['wy'])
        
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
        itera = model.get_iter(paths[0])
        if model.get_value(itera,4) == 1:
            #directory, do nothin', just turn off view
            if __debug__:
                print "[mainwin.py] directory selected"
        else:
            #file, show what you got.
            if __debug__:
                print "[mainwin.py] some other thing selected"
        #}}}
        
    def change_view(self, treeview, path, treecolumn):
        """show information or change directory deep down"""
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
    
    def storeSettings(self):
        """Store window size and pane position in config file (using config object)"""
        #{{{
        if self.conf.confd['savewin']:
            self.conf.confd['wx'], self.conf.confd['wy'] = self.window.get_size()
            
        if self.conf.confd['savepan']:
            hpan = self.pygtkcat.get_widget('hpaned1')
            vpan = self.pygtkcat.get_widget('vpaned1')
            self.conf.confd['h'],self.conf.confd['v'] = hpan.get_position(), vpan.get_position()
            
        self.conf.save()
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
        if self.sbid != 0:
            self.status.remove(self.sbSearchCId, self.sbid)
        self.sbid = self.status.push(self.sbSearchCId, "Calculating number of files in directory tree...")
        for root,kat,plik in os.walk(path):
            for p in plik:
                count+=1
                while gtk.events_pending(): gtk.main_iteration()
        frac = 1.0/count
        
        self.count = 0
        
        def __recurse(path,name,wobj,date=0,frac=0,idWhere=1):
            """recursive scans the path
            path = path string
            name = field name
            wobj = obiekt katalogu
            date = data pliku
            frac - kolejne krok w statusbarze.
            idWhere - simple id parent, or "place" where to add node
            """
            #{{{
            
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
                __recurse(os.path.join(path,i),i,wobj,st.st_mtime,frac,currentid)
                
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
                if wobj.sbid != 0:
                    wobj.status.remove(wobj.sbSearchCId, wobj.sbid)
                wobj.sbid = wobj.status.push(wobj.sbSearchCId, "Scannig: %s" % (os.path.join(root,i)))
                wobj.progress.set_fraction(frac * self.count)
                # PyGTK FAQ entry 23.20
                while gtk.events_pending(): gtk.main_iteration()
                
                self.cur.execute('insert into files(filename, date, size, type) values(?,?,?,?)',(i, st.st_mtime, st.st_size,2))
                self.cur.execute("select seq FROM sqlite_sequence WHERE name='files'")
                currentfileid=self.cur.fetchone()[0]
                self.cur.execute("insert into files_connect(parent,child,depth) values(?,?,?)",(currentfileid, currentfileid, 0))
                if currentid>0:
                    self.cur.execute("insert into files_connect(parent, child, depth) select r1.parent, r2.child, r1.depth + r2.depth + 1 as depth FROM files_connect r1, files_connect r2 WHERE r1.child = ? AND r2.parent = ? ",(currentid, currentfileid))
                self.con.commit()
            #}}}
        
        self.con.commit()
        fileobj = __recurse(path,label,self,0,frac)
        self.unsaved_project = True
        self.__display_main_tree()
        
        if self.sbid != 0:
            self.status.remove(self.sbSearchCId, self.sbid)
        self.sbid = self.status.push(self.sbSearchCId, "Idle")
        
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

