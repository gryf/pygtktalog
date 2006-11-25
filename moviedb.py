#!/usr/bin/python
# -*- coding: iso8859-2 -*-
"""
MovieDB 0.7

features:
    - szukanie po tytule filmu/serii
    - szukanie po nazwie pliku
    
todo:
    - dodatkowe pozycje w menu w zależności od uprawnień
    - edycja plików
    - edycja tytułów
    - edycja innych rzeczy

"""
# TODO: dodać okna/dialogi dodawania/edycji tytułu + menu kontekstowe
# TODO: dodać okna/dialogi dodawania/edycji pliku + menu kontekstowe
# TODO: dodac tablicę w bazie, słownikującą plyty_asarray, lang (sub, dub), nazwy alternatywne triggery do nich
# TODO: opanować dodawanie/usuwanie pozycji w menu głównego

#{{{ podstawowe importy i sprawdzenia
import sys
import os

WRKDIR = sys.argv[0:][0].split('moviedb.py')[0]

if WRKDIR[0] != '/':
    """ścieżka nie jest absolutna"""
    WRKDIR = os.getcwd()+"/"+WRKDIR

try:
    import pygtk
    #tell pyGTK, if possible, that we want GTKv2
    pygtk.require("2.0")
except:
    #Some distributions come with GTK2, but not pyGTK
    pass
try:
    import gtk
    import gtk.glade
except:
    print "You need to install pyGTK or GTKv2 ",
    print "or set your PYTHONPATH correctly."
    print "try: export PYTHONPATH=",
    print "/usr/local/lib/python2.2/site-packages/"
    sys.exit(1)
#now we have both gtk and gtk.glade imported
#Also, we know we are running GTK v2

try:
    from pyPgSQL import PgSQL
    
except:
    print "You need to install pyPgSQL to run this app\nhttp://pypgsql.sourceforge.net/"
    sys.exit(1)

try:
    import pyExcelerator
except:
    print "You need pyExcelerator\nhttp://sourceforge.net/projects/pyexcelerator"
    sys.exit(1)
    
#}}}

try:
    path = os.environ['HOME']
except:
    path = "/tmp"
    
try:
    # przeczytaj plik, o ile istnieje
    f = open("%s/.moviedb" % path,"rw")
    zpliku = f.read()
    f.close()
    p = {}
    zpliku = zpliku.split("\n")
    for i in zpliku:
        i = i.split("\t")
        p[i[0]] = i[1]
    if len(p) == 5:
        USER=p['user']
        PASS=p['pass']
        HOST=p['host']
        DB=p['db']
        CD=p['cdrom']
    else:
        USER="movie"
        PASS="teamsleep"
        HOST="localhost"
        DB="moviedb"
        CD="/mnt/cdrom"
except:
    # w przeciwnym przypadku przjmij wartości domyślne
    USER="movie"
    PASS="teamsleep"
    HOST="localhost"
    DB="moviedb"
    CD="/mnt/cdrom"
    

class SaveAsMDB:
    """pokazuje dialog zapisu(exportu) do pliku""" #{{{
    def __init__(self):
        self.gladefile = WRKDIR + "/glade/moviedb.glade"
    def run(self):
        self.savegld = gtk.glade.XML(self.gladefile, "saveasMDB") 
        self.save = self.savegld.get_widget("saveasMDB")
        self.savegld.get_widget("saveasMDB")
        self.save.set_do_overwrite_confirmation(True)
        
        self.save.set_title("MovieDB - Save as...")
        uri = self.save.set_current_name("moviedb.xls")
        self.result = self.save.run()
        uri = self.save.get_uri()
        self.save.destroy()
        return self.result,uri
        #}}}
    
class SelectFolderMDB:
    """pokazuje dialog wskazania katalogu""" #{{{
    def __init__(self):
        self.gladefile = WRKDIR + "/glade/moviedb.glade"
    def run(self):
        self.selgld = gtk.glade.XML(self.gladefile, "selectFolderMDB") 
        self.sel = self.selgld.get_widget("selectFolderMDB")
        
        self.sel.set_title("MovieDB - Select folder")
        self.result = self.sel.run()
        uri = self.sel.get_uri()
        print uri
        self.sel.destroy()
        return self.result,uri
        #}}}
        
class PrefsMDB:
    """ustawia i zapisuje do pliku ~/.moviedb informacje związane z aplikacją""" #{{{
    def __init__(self):
        self.prefs = {}
        self.gladefile = WRKDIR + "/glade/moviedb.glade"
        self.wPrefs = gtk.glade.XML(self.gladefile,"Prefs")
        self.wPrefs.get_widget("dbuser").set_text(USER)
        self.wPrefs.get_widget("dbpass").set_text(PASS)
        self.wPrefs.get_widget("dbhost").set_text(HOST)
        self.wPrefs.get_widget("dbname").set_text(DB)
        self.wPrefs.get_widget("devdev").set_text(CD)
        dic = {"on_prefsCancel_clicked"     :self.abandonPrefs,\
               "on_prefsSave_clicked"       :self.savePrefs,\
               "on_selectFolder_clicked"    :self.chooseDir}
               
        # podłączenie sygnałów
        self.wPrefs.signal_autoconnect(dic)
        
    def abandonPrefs(self, widget):
        """porzuć edycję preferencji"""
        self.wPrefs.get_widget("Prefs").destroy()
        
    def savePrefs(self,widget):
        """zapisz ustawienia"""
        self.prefs["user"] = self.wPrefs.get_widget("dbuser").get_text()
        self.prefs["pass"] = self.wPrefs.get_widget("dbpass").get_text()
        self.prefs["host"] = self.wPrefs.get_widget("dbhost").get_text()
        self.prefs["db"]   = self.wPrefs.get_widget("dbname").get_text()
        self.prefs["cdrom"] = self.wPrefs.get_widget("devdev").get_text()
        
        try:
            f = open("%s/.moviedb" % path,"w")
            f.write("user\t" + self.prefs['user']\
                    + "\npass\t" + self.prefs['pass']\
                    + "\nhost\t" + self.prefs['host']\
                    + "\ndb\t" + self.prefs['db']\
                    + "\ncdrom\t" + self.prefs['cdrom']\
            )
            f.close()
        except:
            print "Nie można zapisać ustawień!"
            
        # uaktualnij zmienne
        USER=self.prefs['user']
        PASS=self.prefs['pass']
        HOST=self.prefs['host']
        DB=self.prefs['db']
        CD=self.prefs["cdrom"]
        self.wPrefs.get_widget("Prefs").destroy()
        
    def chooseDir(self,widget):
        """wskaż katalog ustawienia"""
        sel = SelectFolderMDB()
        result,selected = sel.run()
        
        if selected[:8] == 'file:///':
            selected = selected[7:]
        self.wPrefs.get_widget("devdev").set_text(selected)
        # uaktualnij zmienne
        DB=selected
        #}}}
        
class StdMSG:
    """pokazuje standartowy dialog - napis i jedne/dwa knefle""" #{{{
    def __init__(self, title="", message="", knefli=2):
        self.gladefile = WRKDIR + "/glade/moviedb.glade"
        self.title = title
        self.message = message
        self.knefli = knefli
    def run(self):
        self.msgld = gtk.glade.XML(self.gladefile, "stdMSG") 
        self.msg = self.msgld.get_widget("stdMSG")
        self.msg.set_title(self.title)
        self.msgld.get_widget("message").set_markup(self.message)
        if self.knefli == 1:
            self.msgld.get_widget("cancelbutton2").hide()
        self.result = self.msg.run()
        self.msg.destroy()
        return self.result
        #}}}

class LoginMDB:
    """pokazuje dialog logowania""" #{{{
    def __init__(self):
        self.gladefile = WRKDIR + "/glade/moviedb.glade"
    def run(self):
        self.logingld = gtk.glade.XML(self.gladefile, "loginMDB") 
        self.login = self.logingld.get_widget("loginMDB")
        try:
            pixBuf = gtk.gdk.pixbuf_new_from_file(WRKDIR + "/pixmaps/login.png")
            self.logingld.get_widget("loginImg").set_from_pixbuf(pixBuf)
        except:
            pass
        
        self.login.set_title("MovieDB - Login")
        self.result = self.login.run()
        l = self.logingld.get_widget("flogin").get_text()
        p = self.logingld.get_widget("fpass").get_text()
        self.login.destroy()
        return self.result,[l,p]
        #}}}

class AboutMDB:
    """pokazuje prosty dialog "o programie" """ #{{{
    def __init__(self):
        self.gladefile = WRKDIR + "/glade/moviedb.glade"
        
    def run(self):
        self.aboutgld = gtk.glade.XML(self.gladefile, "aboutMDB") 
        self.about = self.aboutgld.get_widget("aboutMDB")
        try:
            pixBuf = gtk.gdk.pixbuf_new_from_file(WRKDIR + "/pixmaps/about.png")
            self.aboutgld.get_widget("aboutImg").set_from_pixbuf(pixBuf)
        except:
            pass
        
        self.about.set_title("MovieDB - About")
        self.result = self.about.run()
        self.about.destroy()
        return self.result
        #}}}

class DetailsMDB:
    """Pokazuje okno z informacjami wyciągniętymi z DB na podstawie id tytułu""" #{{{
    def __init__(self, tid=0, perms=0):
        """innicjalizacja obiektu"""
        gladefile=WRKDIR + "/glade/moviedb.glade"
        self.wDetails = gtk.glade.XML(gladefile,"winDetails")
        self.wDetails.get_widget("image1").set_from_file(WRKDIR + "/img/notavail.gif")
        
        # pomocnicze zmienne
        self.perms = perms
        self.typ = '0'
        self.imgIndeks = 1
        
        # inicjalizacja listy z tytułami
        import gobject
        self.lista=self.wDetails.get_widget("pliki")
        self.model=gtk.ListStore(gobject.TYPE_INT,gobject.TYPE_STRING,gobject.TYPE_STRING,\
                                     gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,\
                                     gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,\
                                     gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.lista.set_model(self.model)
        self.lista.set_headers_visible(True)
        
        columns = [[0,"Id"],[1,u"Płyta"],[2,"Nazwa pliku"],\
                  [3,"Sub"],[4,"Dub"],[5,"Rozdz."],\
                  [6,"Video"],[7,"Audio"],[8,"Q"],[9,"Rozm."],[10,'Grupa']]
        
        for col in columns:
            renderer=gtk.CellRendererText()
            column=gtk.TreeViewColumn(col[1],renderer, text=col[0])
            column.set_sort_column_id(col[0])
            column.set_resizable(True)
            if col[0] != 0:
                self.lista.append_column(column)
                
        # inicjalizacja linii statusu
        self.sb=self.wDetails.get_widget("statusDet")
        self.sbSearchCId = self.sb.get_context_id('detailed res')
        self.sbid = 0
        
        # główna robota:
        cx = PgSQL.connect(user=USER, password=PASS, host=HOST, database=DB, client_encoding="iso8859-2")
        c = cx.cursor()
        
        if self.perms != 2:
            typ = 4
        else:
            typ = 0
        
        # {{{ SQL: DetailsMDB#1 wyciągnięcie podstawowych informacji o tytule
        c.execute("SELECT\
                    tytul,\
                    alt,\
                    data_wydania,\
                    ilosc_w_serii,\
                    ilosc_posiadanych,\
                    nazwa_rodzaju,\
                    data_zakonczenia,\
                    a.id_typu\
                from\
                    nazwa_tytulu n\
                    left join tytul a using(id_tytulu)\
                    left join rodzaj r using(id_rodzaju)\
                where\
                    n.id_tytulu = %s\
                    and a.id_typu != %s\
                order by\
                    alt", tid,typ)
        #}}}
        res = c.fetchall()
        
        # {{{ wielki shit do uzupełnienia formularzyka
        if len(res) != 0:
            for row in res:
                if row[1] == False:
                    # główny tytuł
                    if row[7] == 1 or row[7] == 4:
                        self.typ = 'a'
                    else:
                        self.typ = 'f'
                    
                    self.wDetails.get_widget("tytul").set_text(row[0].decode("iso8859-2"))
                    self.wDetails.get_widget("winDetails").set_title('MovieDB - '+row[0].decode("iso8859-2"))
                    # SQL: DetailsMDB#2 pociągnięcie /genre/
                    c.execute("select nazwa from genre_tytul a left join genre g using(id_genre) where id_tytulu=%s order by nazwa",tid)
                    gen = c.fetchall()
                    
                    for g in gen:
                        if (self.wDetails.get_widget("rodzaj").get_text()) == '':
                            self.wDetails.get_widget("rodzaj").set_text(g[0])
                        else:
                            self.wDetails.get_widget("rodzaj").set_text(self.wDetails.get_widget("rodzaj").get_text()+", "+g[0])
                        
                    if (self.wDetails.get_widget("rodzaj").get_text()) == '':
                        self.wDetails.get_widget("rodzaj").hide()
                        self.wDetails.get_widget("label17").hide()
                            
                    if row[2]==None:
                        dadaod = 'unknown'
                    else:
                        dadaod = row[2].strftime("%Y-%m-%d")
                    if row[6]==None:
                        dadado = 'unknown'
                    else:
                        dadado = row[6].strftime("%Y-%m-%d")
                    
                    if dadaod == dadado:
                        self.wDetails.get_widget("label15").set_markup("<b>Data wydania:</b>")
                        self.wDetails.get_widget("data").set_text(dadaod)
                    else:
                        self.wDetails.get_widget("data").set_text(dadaod+"/"+dadado)
                    
                    if row[5] != None:
                        self.wDetails.get_widget("kategoria").set_text(row[5])
                    else:
                        self.wDetails.get_widget("kategoria").hide()
                        self.wDetails.get_widget("label12").hide()
                    
                    if row[3] != None:
                        self.wDetails.get_widget("ilEpizodow").set_text("%d" % row[3])
                    else:
                        self.wDetails.get_widget("ilEpizodow").hide()
                        self.wDetails.get_widget("label13").hide()
                    if row[4] != None:
                        self.wDetails.get_widget("ilPosEpis").set_text("%d" % row[4])
                    else:
                        self.wDetails.get_widget("ilPosEpis").hide()
                        self.wDetails.get_widget("label16").hide()
                else:
                    # tytuły są tytułami alternatywnymi
                    if (self.wDetails.get_widget("tytAlt").get_text()) == '':
                        self.wDetails.get_widget("tytAlt").set_text(row[0].decode("iso8859-2"))
                    else:
                        self.wDetails.get_widget("tytAlt").set_text(self.wDetails.get_widget("tytAlt").get_text()+",\n"+row[0].decode("iso8859-2"))
                    
            # sprawdź czy tutuły alternatywne są puste, jeśli tak, ukryj.
            if(self.wDetails.get_widget("tytAlt").get_text()) == '':
                self.wDetails.get_widget("label11").hide()
                self.wDetails.get_widget("tytAlt").hide()
        #}}}
        # {{{ opanuj obrazki:
        try:
            pixBuf = gtk.gdk.pixbuf_new_from_file(WRKDIR + "/img/%c%d_1.jpg" % (self.typ,tid))
            self.wDetails.get_widget("image1").set_from_pixbuf(pixBuf)
            # podłącz sygnały do guzików, wyłącznie w przypadku istnienia obrazków
            #  "on button1_clicked" : (self.button1_clicked, arg1,arg2)
            lista = {"on_popBut_clicked" : (self.prevPict, self.typ, tid),\
                     "on_nasBut_clicked" : (self.nextPict, self.typ, tid)}
            self.wDetails.signal_autoconnect(lista)
        except:
            self.wDetails.get_widget("image1").set_from_file(WRKDIR + "/img/notavail.gif")
            self.wDetails.get_widget("nasBut").hide()
            self.wDetails.get_widget("popBut").hide()
            self.wDetails.get_widget("hseparator1").hide()
        #}}}
        # {{{ pokaż listę plików
        c = cx.cursor()
        
        # SQL: DetailsMDB#3 pokaż listę plików
        c.execute("SELECT\
                p.id_pliku,\
                aktywny,\
                nazwa_pliku,\
                format,\
                rozdz,\
                vcodec,\
                acodec,\
                rozmiar,\
                jakosc,\
                nr_plyty,\
                nr_pudelka,\
                lang_asarray(p.id_pliku::text,'sub'::text),\
                lang_asarray(p.id_pliku::text,'dub'::text),\
                gp.short\
		from\
			plik p\
				left join plyta y using(id_pliku)\
                left join grupa_plik g using(id_pliku)\
                left join grupa gp using(id_grupy)\
		where\
			id_tytulu=%s", tid)
        
        res = c.fetchall()
        
        # pokazanie liości wyników a linii stratusu
        if self.sbid != 0:
            """jeśli jest jakiś mesedż, usuń go"""
            self.sb.remove(self.sbSearchCId, self.sbid)
        liczba_wynikow = u"Ilość plików należących do tytułu: %d" % len(res)
        self.sbid = self.sb.push(self.sbSearchCId, liczba_wynikow)
        
        if len(res)>0:
            # pokazanie listy
            self.model.clear()
            for i in res:
                self.insert_row(self.model,i[0],"%s/%s" % (i[9],i[10]),i[2].decode("iso8859-2"),i[11],i[12],i[4],i[5],i[6],i[8],i[7],i[13])
                
            #model.set_sort_column_id(1,gtk.SORT_ASCENDING)
        #}}}
        
    # SYGNAŁY
    def prevPict(self, widget, typ, tid):
        """pokaż poprzedni obrazek, jeśli jest"""
        if self.imgIndeks > 1:
            self.imgIndeks-=1
            try:
                pixBuf = gtk.gdk.pixbuf_new_from_file(WRKDIR + "/img/%c%d_%d.jpg" % (typ,tid,self.imgIndeks))
                self.wDetails.get_widget("image1").clear()
                self.wDetails.get_widget("image1").set_from_pixbuf(pixBuf)
            except:
                pass
    
    def nextPict(self, widget, typ, tid):
        """pokaż kolejny obrazek, jeśli jest"""
        if self.imgIndeks < 5:
            self.imgIndeks+=1
            try:
                pixBuf = gtk.gdk.pixbuf_new_from_file(WRKDIR + "/img/%c%d_%d.jpg" % (typ,tid,self.imgIndeks))
                self.wDetails.get_widget("image1").clear()
                self.wDetails.get_widget("image1").set_from_pixbuf(pixBuf)
            except:
                pass
                
    # funkcje pomocnicze
    def insert_row(self,model,pid,plyta,nazwa_pliku,sub,dub,rozdz,vid,aud,q,rozm,grup):
        myiter=model.insert_after(None,None)
        model.set_value(myiter,0,pid)
        model.set_value(myiter,1,plyta)
        model.set_value(myiter,2,nazwa_pliku)
        model.set_value(myiter,3,sub)
        model.set_value(myiter,4,dub)
        model.set_value(myiter,5,rozdz)
        model.set_value(myiter,6,vid)
        model.set_value(myiter,7,aud)
        model.set_value(myiter,8,q)
        model.set_value(myiter,9,rozm)
        model.set_value(myiter,10,grup)
        #}}}
        
class MovieDB:
    """pokazująca główne okno aplikacji, pozwalająca na przeszukiwanie wśród plików i tytułów i wyświetlająca wynik wyszukiwania""" #{{{
    def __init__(self, perms=0):
        
        self.perms = perms
        self.gladefile=WRKDIR + "/glade/moviedb.glade"
        self.wTree=gtk.glade.XML(self.gladefile,"mainWin")
        
        # sygnały:
        dic = {"on_mainWin_destroy"     :(gtk.main_quit),\
               "on_quit1_activate"      :(gtk.main_quit),\
               "on_szukaj_clicked"      :(self.searchdb,self.perms),\
               "on_szukPat_activate"    :(self.searchdb,self.perms),\
               "on_lista_row_activated" :(self.szczegoly,self.perms),\
               "on_about1_activate"     :self.oprogramie,\
               "on_cut1_activate"       :self.showPrefs,\
               "on_save_as1_activate"    :self.exportToXLS}
               
        # inicjalizacja dodatkowych pozycji w menu, jeśli uprawnienia pozwalają
        if self.perms == 2:
            pass
            #self.wTree.get_widget("mainMenu").
        
        # podłączenie sygnałów
        self.wTree.signal_autoconnect(dic)
        
        # inicjalizacja combo boxów
        self.treeview=self.wTree.get_widget("pattMatch").set_active(0)
        self.treeview=self.wTree.get_widget("typ").set_active(0)
        if self.perms ==2:
            self.treeview=self.wTree.get_widget("typ").append_text('XXX')
        # inicjalizacja listy z tytułami
        import gobject
        self.treeview=self.wTree.get_widget("lista")
        self.treemodel=gtk.TreeStore(gobject.TYPE_INT,gobject.TYPE_STRING,gobject.TYPE_INT,\
                                     gobject.TYPE_INT,gobject.TYPE_STRING,gobject.TYPE_STRING,\
                                     gobject.TYPE_STRING)
        self.treeview.set_model(self.treemodel)
        self.treeview.set_headers_visible(True)
        
        columns = [[0,"Id"],[1,u"Tytuł"],[2,u"Ilość"],[3,"Posiadanych"],[4,"Rok"],[5,"Typ"],[6,"Plyty"]]
        
        for col in columns:
            renderer=gtk.CellRendererText()
            column=gtk.TreeViewColumn(col[1],renderer, text=col[0])
            column.set_sort_column_id(col[0])
            column.set_resizable(True)
            if col[0] != 0:
                self.treeview.append_column(column)
        
        # inicjalizacja linii statusu
        self.sb=self.wTree.get_widget("statusbar")
        self.sbSearchCId = self.sb.get_context_id('search res')
        self.sbid = 0
        
        return
            
    def insert_row(self,model,parent,tid,tytul,il,pos,rok,typ,plyty):
        myiter=model.insert_after(parent,None)
        model.set_value(myiter,0,tid)
        model.set_value(myiter,1,tytul)
        model.set_value(myiter,2,il)
        model.set_value(myiter,3,pos)
        model.set_value(myiter,4,rok)
        model.set_value(myiter,5,typ)
        model.set_value(myiter,6,plyty)
        return myiter
        
    #####CALLBACKS
    def szczegoly(self,treeview,path,view_column,perms=0):
        """pokaż szczegóły w nowym oknie.""" # {{{
        win = DetailsMDB(treeview.get_model().get_value(treeview.get_model().get_iter(path),0),perms)
        #}}}
        
    def oprogramie(self, widget):
        """Pokazuje dialog about""" #{{{
        about = AboutMDB()
        result = about.run()
        #}}}
		
    def showPrefs(self, widget):
        """Pokazuje okno preferencji""" #{{{
        prefs = PrefsMDB()
        #}}}
        
    def searchdb(self,widget,perms=0):
        """ułóż zapytanie i wypluj wyniki do treeview""" #{{{
        if self.wTree.get_widget("pattMatch").get_active() == 3:
            pattern=self.wTree.get_widget("szukPat").get_text()
        elif self.wTree.get_widget("pattMatch").get_active() == 2:
            pattern="%" + self.wTree.get_widget("szukPat").get_text()
        elif self.wTree.get_widget("pattMatch").get_active() == 1:
            pattern=self.wTree.get_widget("szukPat").get_text() + "%"
        else:
            pattern="%" + self.wTree.get_widget("szukPat").get_text() + "%"
            
        cx = PgSQL.connect(user=USER, password=PASS, host=HOST, database=DB, client_encoding="iso8859-2")
        c = cx.cursor()
        if self.wTree.get_widget("czalt").get_active():
            klon = False
        else:
            klon = True
        
        # szukaj wg typu:
        # NOTE: daj tu to, co potrzeba
        anime,filmy,kreskowki,xxx,typ = self.getType()
        if self.wTree.get_widget("radn").get_active():
            # SQL: zapytanie zbierające tytuły filmów po kluczu nazw plików
            # TODO: zrobić tablicę przechowującą nr płyt (najlepiej triggerze)
            c.execute("SELECT distinct\
                  a.id_tytulu,\
                  n.tytul,\
                  alt,\
                  to_char (data_wydania,'YYYY'),\
                  case\
                    when\
                        ilosc_w_serii is null then 0\
                    else\
                        ilosc_w_serii\
                  end,\
                  case\
                    when\
                        ilosc_posiadanych is null then 0\
                    else\
                        ilosc_posiadanych\
                  end,\
                  nazwa_typu,\
                  plyty_asstring(a.id_tytulu::text)\
            from\
                nazwa_tytulu as n\
                left join tytul a using(id_tytulu)\
                left join typ as t using(id_typu)\
                left join plik p using(id_tytulu)\
            where\
                (alt is false or alt is %s)\
                and nazwa_pliku ilike %s\
                and id_typu in (%s, %s, %s, %s)\
                and id_typu != %s\
            order by\
                id_tytulu, alt",(klon,pattern.encode("iso8859-2"),anime,xxx,filmy,kreskowki,typ))
        else:
        # SQL: zapytanie zbierające tytuły filmów
            c.execute("SELECT \
                  a.id_tytulu,\
                  n.tytul,\
                  alt,\
                  to_char (data_wydania,'YYYY'),\
                  case\
                    when\
                        ilosc_w_serii is null then 0\
                    else\
                        ilosc_w_serii\
                  end,\
                  case\
                    when\
                        ilosc_posiadanych is null then 0\
                    else\
                        ilosc_posiadanych\
                  end,\
                  nazwa_typu,\
                  plyty_asstring(a.id_tytulu::text)\
            from\
                nazwa_tytulu as n\
                left join tytul a using(id_tytulu)\
                left join typ as t using(id_typu)\
            where\
                (alt is false or alt is %s)\
                and tytul ilike %s\
                and id_typu in (%s, %s, %s, %s)\
                and id_typu != %s\
            order by\
                id_tytulu, alt",(klon,pattern.encode("iso8859-2"),anime,xxx,filmy,kreskowki,typ))
        
        res = c.fetchall()
        cx.close()
        
        # pokazanie liości wyników a linii stratusu
        if self.sbid != 0:
            """jeśli jest jakiś mesedż, usuń go"""
            self.sb.remove(self.sbSearchCId, self.sbid)
        liczba_wynikow = u"Ilość znalezionych rekordów: %d" % len(res)
        self.sbid = self.sb.push(self.sbSearchCId, liczba_wynikow)
        
        if len(res)>0:
            # pokazanie listy
            model=self.treemodel
            self.treemodel.clear()
            if self.wTree.get_widget("showAsTree").get_active():
                ido=0
                for i in res:
                    if i[2] == True and ido == i[0]:
                        self.insert_row(model,iterobj,i[0],i[1].decode("iso8859-2"),i[4],i[5],i[3],i[6],i[7])
                    else:
                        iterobj = self.insert_row(model,None,i[0],i[1].decode("iso8859-2"),i[4],i[5],i[3],i[6],i[7])
                    ido = i[0]
            else:
                for i in res:
                    self.insert_row(model,None,i[0],i[1].decode("iso8859-2"),i[4],i[5],i[3],i[6],i[7])
                    
            #model.set_sort_column_id(1,gtk.SORT_ASCENDING)
            
            # pokazanie wyników w tabelce
            self.wTree.get_widget("scrListy").show()
            self.treeview.expand_all()
        else:
            self.wTree.get_widget("scrListy").hide()
    #}}}
    def getType(self):
        """zdejmuje typ dla zapytania SQL"""
        typ = self.wTree.get_widget("typ").get_active()
        if typ == 4:
            anime = 4
            filmy = 4
            kreskowki = 4
            xxx = 4
        elif typ == 3:
            anime = 3
            filmy = 3
            kreskowki = 3
            xxx = 3
        elif typ == 2:
            anime = 2
            filmy = 2
            kreskowki = 2
            xxx = 2
        elif typ == 1:
            anime = 1
            filmy = 1
            kreskowki = 1
            xxx = 1
        else:
            anime = 1
            filmy = 2
            kreskowki = 3
            xxx = 4
        if self.perms !=2:
            typ=4
        else:
            typ=0
        
        return anime,filmy,kreskowki,xxx,typ
        
    def exportToXLS(self,widget):
        """eksportuj bazę do arkusza xls""" #{{{
        fIter = self.treemodel.get_iter_first()
        ajdiki = "(0"
        if fIter!=None:
            ids = []
            ids.append(self.treemodel.get_value(fIter,0))
            nIter = self.treemodel.iter_next(fIter)
            while nIter!=None:
                ids.append(self.treemodel.get_value(nIter,0))
                nIter = self.treemodel.iter_next(nIter)
            
            ajl = []
            for i in set(ids):
                ajl.append(i)
                ajdiki+=",%s" % i
        else:
            pass
        ajdiki+=")"
        idnum = len(ajl)
        sa = SaveAsMDB()
        result,uri = sa.run()
        if (result == gtk.RESPONSE_OK):
            # open(uri[7:],"w")
            import pyExcelerator as X
            w = X.Workbook()
            X.UnicodeUtils.DEFAULT_ENCODING = 'cp1250'
            
            anime,filmy,kreskowki,xxx,typ = self.getType()
            
            cx = PgSQL.connect(user=USER, password=PASS, host=HOST, database=DB, client_encoding="iso8859-2")
            c = cx.cursor()
            sql = "select\
				p.id_pliku,\
				case when nr_plyty is null then 'brak' else nr_plyty end,\
				nazwa_pliku,\
				rozdz,\
				vcodec,\
				acodec,\
				jakosc,\
				rozmiar,\
				p.id_tytulu,\
                to_char (p.data_dodania,'YYYY-MM-DD HH24:MM:SS'),\
                lang_asarray(p.id_pliku::text,'dub'),\
                lang_asarray(p.id_pliku::text,'sub')\
			from\
				plik p\
					left join plyta l using(id_pliku)\
					left join tytul t using(id_tytulu)\
			where\
					p.aktywny is true\
				and\
					t.id_typu in (%s, %s, %s, %s)" % (anime,filmy,kreskowki,xxx)
            sql+=" and\
                    t.id_typu != %s" % typ
            sql+=" and\
                    p.id_tytulu in ("+ ", ".join(["%s"] * idnum) + ")\
			order by\
				nazwa_pliku"
            
            c.execute(sql, ajl)
            pliki = c.fetchall()
            
            
            row = 0
            sheet = w.add_sheet("Anime")
            
            # nagłówki
            sheet.write(row, 0, u"tytuł anime".encode("cp1250"))
            sheet.write(row, 1, u"nr płyty".encode("cp1250"))
            sheet.write(row, 2, "nazwa pliku".encode("cp1250"))
            sheet.write(row, 3, "dub".encode("cp1250"))
            sheet.write(row, 4, "sub".encode("cp1250"))
            sheet.write(row, 5, "rozdz".encode("cp1250"))
            sheet.write(row, 6, "vcodec".encode("cp1250"))
            sheet.write(row, 7, "acodec".encode("cp1250"))
            sheet.write(row, 8, u"jakość".encode("cp1250"))
            sheet.write(row, 9, "rozmiar pliku".encode("cp1250"))
            sheet.write(row, 10, "typ".encode("cp1250"))
            sheet.write(row, 11, "data".encode("cp1250"))
            sheet.write(row, 12, u"ilość odc.".encode("cp1250"))
            sheet.write(row, 13, u"ilość posiadanych".encode("cp1250"))
            sheet.write(row, 14, "data dodania pliku".encode("cp1250"))
            row+=1
            
            idanime="0"
            for plik in pliki:
                if plik[9]!=idanime:
                    sql="SELECT\
                                tytul,\
                                alt,\
                                nazwa_rodzaju,\
                                case when data_wydania is null then 'brak' else to_char (data_wydania,'YYYY-MM-DD') end,\
                                data_zakonczenia,\
                                ilosc_w_serii,\
                                ilosc_posiadanych\
                            from\
                                nazwa_tytulu as n\
                                    left join tytul a using(id_tytulu)\
                                    left join rodzaj r using(id_rodzaju)\
                            where\
                                    a.id_tytulu=%s\
                                and\
                                    a.id_typu in (%s, %s, %s, %s)\
                                and\
                                    a.id_typu != %s\
                                and\
                                    alt is false\
                            order by\
                                tytul" % (plik[8],anime,filmy,kreskowki,xxx,typ)
                    c.execute(sql)
                    tytuly = c.fetchone()
                print tytuly[0]
                sheet.write(row, 0, tytuly[0].decode("iso8859-2").encode("cp1250"))
                sheet.write(row, 1, plik[1].encode("cp1250"))
                sheet.write(row, 2, plik[2].decode("iso8859-2").encode("cp1250"))
                sheet.write(row, 3, plik[10].encode("cp1250"))
                sheet.write(row, 4, plik[11].encode("cp1250"))
                sheet.write(row, 5, plik[3].encode("cp1250"))
                sheet.write(row, 6, plik[4].encode("cp1250"))
                sheet.write(row, 7, plik[5].encode("cp1250"))
                sheet.write(row, 8, plik[6])
                sheet.write(row, 9, plik[7])
                sheet.write(row, 10, "typ".encode("cp1250"))
                sheet.write(row, 11, tytuly[3])
                sheet.write(row, 12, tytuly[5])
                sheet.write(row, 13, tytuly[6])
                sheet.write(row, 14, plik[9].encode("cp1250"))
                row+=1
            w.save(uri[7:])
            cx.close()
        #}}}
#}}}
    
# NOTE: koniec deklaracji klas. główny program:
petla = 0
perms = 0

while petla == 0:
    # {{{ pokazanie dialogu logowania w pętli
    login = LoginMDB()
    result,loginPair = login.run()
    
    #sprawdzenie co też użytkownik wpisał i dokonanie odpowiedniego zachowania
    if (result == gtk.RESPONSE_OK):
        # w przypadku naciśnięcia OK, pobranie z DB uprawnienia, jeśli login/hasło się zgadza
        cx = PgSQL.connect(user=USER, password=PASS, host=HOST, database=DB, client_encoding="iso8859-2")
        c = cx.cursor()
        c.execute("SELECT\
                uprawnienia\
            from\
                users\
            where\
                login = %s\
                and password = md5(%s)\
                ", loginPair[0],loginPair[1])
        perms = c.fetchone()
        cx.close()
        
        if perms==None:
            # zły login lub hasło
            m = StdMSG(u"MovieDB - Błąd logowania",u"Nieprawidłowy login lub hasło.\n",1)
            m.run()
        else:
            # zapytanie zwróciło nie None; wychodzimy z pętli while.
            petla = 1
            perms = perms[0]
    elif (result == gtk.RESPONSE_CANCEL):
        # user nacisnął cancel, więc nie chce, lub ne może się zalogować. sprawdzamy jak jest.
        # pokazanie dialogu z pytaniem
        m = StdMSG("MovieDB - Pytanie",u"Jesteś pewien, że <b>nie chcesz</b> się logować?\n")
        res = m.run()
        if(res == gtk.RESPONSE_OK):
            # jeśli jest pewny, wychodzimy z pętli while. jeśli nie, nic nie robimy,
            # okno logowanie pojawi się przy powtórnym obrocie pętli.
            petla = 1
    else:
        # user ubił okno logowania, lub pociągnął z krzyża, lub do dialogu został wysłany inny sygnał.
        petla = 2
        #}}}

if petla != 2:
    # w przypadku pociągnięcia z krzyża wychodzimy z aplikacji, w pozostałych przypadkach uruchomione zostaje główne okno.
    app=MovieDB(perms)
    try:
        gtk.main()
    except KeyboardInterrupt:
        gtk.main_quit

