import pygtk; pygtk.require('2.0')
import gtk

import EXIF
import Image
import os
import shutil
from datetime import datetime

class Thumbnail(object):
    def __init__(self, filename=None, x=160, y=120, root='thumbnails', base=''):
        self.root = root
        self.x = x
        self.y = y
        self.filename = filename
        self.base = base
        
    def save(self, image_id):
        """Save thumbnail into specific directory structure
        return full path to the file and exif object or None"""
        filepath = os.path.join(self.base, self.__get_and_make_path(image_id))
        f = open(self.filename, 'rb')
        exif = None
        returncode = -1
        try:
            exif = EXIF.process_file(f)
            f.close()
            if exif.has_key('JPEGThumbnail'):
                thumbnail = exif['JPEGThumbnail']
                f = open(filepath,'wb')
                f.write(thumbnail)
                f.close()
                if exif.has_key('Image Orientation'):
                    orientation = exif['Image Orientation'].values[0]
                    if orientation > 1:
                        t = "/tmp/thumb%d.jpg" % datetime.now().microsecond
                        im_in = Image.open(filepath)
                        im_out = None
                        if orientation == 8:
                            im_out = im_in.transpose(Image.ROTATE_90)
                        elif orientation == 6:
                            im_out = im_in.transpose(Image.ROTATE_270)
                        if im_out:
                            im_out.save(t, 'JPEG')
                            shutil.move(t, filepath)
                        else:
                            f.close()
                returncode = 0
            else:
                im = self.__scale_image(True)
                if im:
                    im.save(filepath, "JPEG")
                    returncode = 1
        except:
            f.close()
            im = self.__scale_image(True)
            if im:
                im.save(filepath, "JPEG")
                returncode = 2
        return filepath, exif, returncode
        
    # private class functions
    def __get_and_make_path(self, img_id):
        """Make directory structure regards of id
        and return filepath WITHOUT extension"""
        try: os.mkdir(self.root)
        except: pass
        h = hex(img_id)
        if len(h[2:])>6:
            try: os.mkdir(os.path.join(self.root, h[2:4]))
            except: pass
            try: os.mkdir(os.path.join(self.root, h[2:4], h[4:6]))
            except: pass
            path = os.path.join(self.root, h[2:4], h[4:6], h[6:8])
            try: os.mkdir(path)
            except: pass
            img = "%s.%s" % (h[8:], 'jpg')
        elif len(h[2:])>4:
            try: os.mkdir(os.path.join(self.root, h[2:4]))
            except: pass
            path = os.path.join(self.root, h[2:4], h[4:6])
            try: os.mkdir(path)
            except: pass
            img = "%s.%s" % (h[6:], 'jpg')
        elif len(h[2:])>2:
            path = os.path.join(self.root, h[2:4])
            try: os.mkdir(path)
            except: pass
            img = "%s.%s" %(h[4:], 'jpg')
        else:
            path = self.root
            img = "%s.%s" %(h[2:], 'jpg')
        return(os.path.join(self.root, img))
        
    def __scale_image(self, factor=False):
        """generate scaled Image object for given file
        args:
            factor - if False, adjust height into self.y
                     if True, use self.x for scale portrait pictures height.
            returns Image object, or False
        """
        try:
            im = Image.open(self.filename).convert('RGB')
        except:
            return False
        x, y = im.size
        
        if x > self.x or y > self.y:
            if x==y:
                # square
                imt = im.resize((self.y, self.y), Image.ANTIALIAS)
            elif x > y:
                # landscape
                if int(y/(x/float(self.x))) > self.y:
                    # landscape image: height is non standard
                    self.x1 = int(float(self.y) * self.y / self.x)
                    if float(self.y) * self.y / self.x - self.x1 > 0.49:
                        self.x1 += 1
                    imt = im.resize(((int(x/(y/float(self.y))),self.y)),Image.ANTIALIAS)
                elif x/self.x==y/self.y:
                    # aspect ratio ok
                    imt = im.resize((self.x, self.y), Image.ANTIALIAS)
                else:
                    imt = im.resize((self.x,int(y/(x/float(self.x)))), 1)
            else:
                # portrait
                if factor:
                    if y>self.x:
                        imt = im.resize(((int(x/(y/float(self.x))),self.x)),Image.ANTIALIAS)
                    else:
                        imt = im
                else:
                    self.x1 = int(float(self.y) * self.y / self.x)
                    if float(self.y) * self.y / self.x - self.x1 > 0.49:
                        self.x1 += 1
                    
                    if x/self.x1==y/self.y:
                        # aspect ratio ok
                        imt = im.resize((self.x1,self.y),Image.ANTIALIAS)
                    else:
                        imt = im.resize(((int(x/(y/float(self.y))),self.y)),Image.ANTIALIAS)
            return imt
        else:
            return im

class Image_Example(object):

    def pressButton(self, widget, data=None):
        print "Pressed"

    def delete_event(self, widget, event, data=None):
        print "delete event occured"

        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)

        self.button = gtk.Button()
        self.button.connect("clicked", self.pressButton, None)
        self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
        
        
        
        root, dirs, files = os.walk('/home/gryf/t/t').next()
        count = 0
        for i in files:
            count+=1
            path, exif, success = Thumbnail(os.path.join(root, i), base='/home/gryf/t/t').save(count)
            if exif:
                print path, len(exif), success
            if success != -1:
                p = path
                
        self.image = gtk.Image()
        self.image.set_from_file(os.path.join(root, path))
        self.image.show()
        
        pb = self.image.get_pixbuf()
        print pb.get_width(), pb.get_height()

        self.button.add(self.image)
        self.window.add(self.button)
        self.button.show()
        self.window.show()
        
        

    def main(self):
        gtk.main()


if __name__ == '__main__':

    Image_Example().main()

