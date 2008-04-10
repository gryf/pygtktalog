import re
import EXIF
class ParseExif(object):
    def __init__(self, exif_dict=None, exif_file=None):
        self.camera = None
        self.date = None
        self.aperture = None
        self.exposure_program = None
        self.exposure_bias = None
        self.iso = None
        self.focal_length = None
        self.subject_distance = None
        self.metering_mode = None
        self.flash = None
        self.light_source = None
        self.resolution = None
        self.orientation = None
        self.exif_dict = exif_dict
        if not self.exif_dict:
            try:
                f = open(exif_file, 'rb')
                e = EXIF.process_file(f)
                if len(e.keys()) >0:
                    self.exif_dict = e 
                f.close()
            except:
                pass
    def parse(self):
        try:
            self.camera = "%s" % self.exif_dict['Image Make']
            self.camera = self.camera.strip()
        except: pass
        try:
            model = "%s" % self.exif_dict['Image Model']
            self.camera += ", " + model.strip()
        except: pass
        
        try:
            self.date = "%s" % self.exif_dict['EXIF DateTimeOriginal']
            p = re.compile('[\d,:]+')
            if not p.match(self.date):
                self.date = None
        except: pass
        
        try:
            self.aperture = "%s" % self.exif_dict['EXIF FNumber']
            if len(self.aperture.split("/")) == 2:
                self.aperture += '.'
                self.aperture = "%.1f" % eval(self.aperture)
            self.aperture = "f/%.1f" % float(self.aperture)
            self.aperture = self.aperture.replace('.',',')
        except: pass
        
        try: self.exposure_program = "%s" % self.exif_dict['EXIF ExposureProgram']
        except: pass
        
        try:
            self.exposure_bias = "%s" % self.exif_dict['EXIF ExposureBiasValue']
            if len(self.exposure_bias.split("/")) == 2:
                self.exposure_bias += '.'
                self.exposure_bias = "%.1f" % eval(self.exposure_bias)
            self.exposure_bias = "%.1f" % float(self.exposure_bias)
            self.exposure_bias = self.exposure_bias.replace('.',',')
        except: pass
        
        try: self.iso = "%s" % self.exif_dict['EXIF ISOSpeedRatings']
        except: pass
        
        try:
            self.focal_length = "%s" % self.exif_dict['EXIF FocalLength']
            if len(self.focal_length.split("/")) == 2:
                self.focal_length += '.'
                self.focal_length = "%.2f" % eval(self.focal_length)
            self.focal_length = "%.2f mm" % float(self.focal_length)
            self.focal_length = self.focal_length.replace('.',',')
        except: pass
        
        try:
            self.subject_distance = "%s" % self.exif_dict['EXIF SubjectDistance']
            if len(self.subject_distance.split("/")) == 2:
                self.subject_distance += '.'
                self.subject_distance = "%.3f" % eval(self.subject_distance)
            self.subject_distance = "%.3f m" % float(self.subject_distance)
            self.subject_distance = self.subject_distance.replace('.',',')
        except: pass
        
        try: self.metering_mode = "%s" % self.exif_dict['EXIF MeteringMode']
        except: pass
        
        try: self.flash = "%s" % self.exif_dict['EXIF Flash']
        except: pass
        
        try: self.light_source = "%s" % self.exif_dict['EXIF LightSource']
        except: pass
        
        try: self.resolution = "%s" % self.exif_dict['Image XResolution']
        except: pass
        try: self.resolution = self.resolution + " x %s" % self.exif_dict['Image YResolution']
        except: pass
        try: self.resolution = self.resolution + " (%s)" % self.exif_dict['Image ResolutionUnit']
        except: pass
        
        try: self.orientation = "%s" % self.exif_dict['Image Orientation']
        except: pass
        
        return (self.camera, self.date, self.aperture, self.exposure_program, self.exposure_bias, self.iso, self.focal_length, self.subject_distance, self.metering_mode, self.flash, self.light_source, self.resolution, self.orientation)
        #print self.date #self.camera, self.date, self.aperture, self.exposure_program, self.exposure_bias, self.iso, self.focal_length, self.subject_distance, self.metering_mode, self.flash, self.light_source, self.resolution, self.flash, self.orientation
