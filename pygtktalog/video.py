"""
    Project: pyGTKtalog
    Description: Gather video file information, make "screenshot" with content
                 of the movie file. Uses external tools like mplayer and
                 ImageMagick tools (montage, convert).
    Type: lib
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-04-04
"""
import os
import shutil
from tempfile import mkdtemp, mkstemp
import math

import Image
from pygtktalog.misc import float_to_string


class Video(object):
    """Class for retrive midentify script output and put it in dict.
    Usually there is no need for such a detailed movie/clip information.
    Midentify script belongs to mplayer package.
    """

    def __init__(self, filename, out_width=1024):
        """
        Init class instance.
        Arguments:
            @filename - Filename of a video file (required).
            @out_width - width of final image to be scaled to.
        """
        self.filename = filename
        self.out_width = out_width
        self.tags = {}

        output = self._get_movie_info()

        attrs = {'ID_VIDEO_WIDTH': ['width', int],
                 'ID_VIDEO_HEIGHT': ['height', int],
                 # length is in seconds
                 'ID_LENGTH': ['length', lambda x: int(x.split(".")[0])],
                 'ID_DEMUXER': ['container', self._return_lower],
                 'ID_VIDEO_FORMAT': ['video_format', self._return_lower],
                 'ID_VIDEO_CODEC': ['video_codec', self._return_lower],
                 'ID_AUDIO_CODEC': ['audio_codec', self._return_lower],
                 'ID_AUDIO_FORMAT': ['audio_format', self._return_lower],
                 'ID_AUDIO_NCH':  ['audio_no_channels', int],}
                 # TODO: what about audio/subtitle language/existence?

        for key in output:
            if key in attrs:
                self.tags[attrs[key][0]] = attrs[key][1](output[key])

        if 'length' in self.tags and self.tags['length'] > 0:
            hours = self.tags['length'] / 3600
            seconds = self.tags['length'] - hours * 3600
            minutes = seconds / 60
            seconds -= minutes * 60
            length_str = "%02d:%02d:%02d" % (hours, minutes, seconds)
            self.tags['duration'] = length_str

    def capture(self):
        """
        Extract images for given video filename and montage it into one, big
        picture, similar to output from Windows Media Player thing, but without
        captions and time (who need it anyway?).

        Returns: image filename or None

        NOTE: You should remove returned file manually, or move it in some
        other place, otherwise it stays in filesystem.
        """

        if not (self.tags.has_key('length') and self.tags.has_key('width')):
            # no length or width
            return None

        if not (self.tags['length'] >0 and self.tags['width'] >0):
            # zero length or wight
            return None

        # Calculate number of pictures. Base is equivalent 72 pictures for
        # 1:30:00 movie length
        scale = int(10 * math.log(self.tags['length'], math.e) - 11)

        if scale < 1:
            return None

        no_pictures = self.tags['length'] / scale

        if no_pictures > 8:
            no_pictures = (no_pictures / 8 ) * 8 # only multiple of 8, please.
        else:
            # for really short movies
            no_pictures = 4

        tempdir = mkdtemp()
        file_desc, image_fn = mkstemp()
        os.close(file_desc)
        self._make_captures(tempdir, no_pictures)
        #self._make_montage(tempdir, image_fn, no_pictures)
        self._make_montage3(tempdir, image_fn, no_pictures)

        shutil.rmtree(tempdir)
        return image_fn


    def _get_movie_info(self):
        """
        Gather movie file information with midentify shell command.
        Returns: dict of command output. Each dict element represents pairs:
                 variable=value, for example output from midentify will be:

                     ID_VIDEO_ID=0
                     ID_AUDIO_ID=1
                     ....
                     ID_AUDIO_CODEC=mp3
                     ID_EXIT=EOF

                 so method returns dict:

                     {'ID_VIDEO_ID': '0',
                      'ID_AUDIO_ID': 1,
                      ....
                      'ID_AUDIO_CODEC': 'mp3',
                      'ID_EXIT': 'EOF'}
        """
        output = os.popen('midentify "%s"' % self.filename).readlines()
        return_dict = {}

        for line in output:
            line = line.strip()
            key = line.split('=')
            if len(key) > 1:
                return_dict[key[0]] = line.replace("%s=" % key[0], "")
        return return_dict

    def _make_captures(self, directory, no_pictures):
        """
        Make screens with mplayer into given directory
        Arguments:
            @directory - full output directory name
            @no_pictures - number of pictures to take
        """
        step = float(self.tags['length']/(no_pictures + 1))
        current_time = 0
        for dummy in range(1, no_pictures + 1):
            current_time += step
            time = float_to_string(current_time)
            cmd  = "mplayer \"%s\" -ao null -brightness 0 -hue 0 " \
            "-saturation 0 -contrast 0 -vf-clr -vo jpeg:outdir=\"%s\" -ss %s" \
            " -frames 1 2>/dev/null"
            os.popen(cmd % (self.filename, directory, time)).readlines()

            shutil.move(os.path.join(directory, "00000001.jpg"),
                        os.path.join(directory, "picture_%s.jpg" % time))

    def _make_montage2(self, directory, image_fn, no_pictures):
        """
        Generate one big image from screnshots and optionally resize it. Use
        external tools from ImageMagic package to arrange and compose final
        image. First, images are prescaled, before they will be montaged.

        Arguments:
            @directory - source directory containing images
            @image_fn - destination final image
            @no_pictures - number of pictures
        timeit result:
            python /usr/lib/python2.6/timeit.py -n 1 -r 1 'from pygtktalog.video import Video; v = Video("/home/gryf/t/a.avi"); v.capture()'
            1 loops, best of 1: 25 sec per loop
        """
        row_length = 4
        if no_pictures < 8:
            row_length = 2

        if not (self.tags['width'] * row_length) > self.out_width:
            for i in (8, 6, 5):
                if (no_pictures % i) == 0 and \
                   (i * self.tags['width']) <= self.out_width:
                    row_length = i
                    break

        coef = float(self.out_width - row_length * 4) / (self.tags['width'] * row_length)
        scaled_width = int(self.tags['width'] * coef)

        # scale images
        for fname in os.listdir(directory):
            cmd = "convert -scale %d %s %s_s.jpg"
            os.popen(cmd % (scaled_width, os.path.join(directory, fname),
                            os.path.join(directory, fname))).readlines()
            shutil.move(os.path.join(directory, fname + "_s.jpg"),
                        os.path.join(directory, fname))


        tile = "%dx%d" % (row_length, no_pictures / row_length)

        _curdir = os.path.abspath(os.path.curdir)
        os.chdir(directory)

        # composite pictures
        # readlines trick will make to wait for process end
        cmd = "montage -tile %s -geometry +2+2 picture_*.jpg montage.jpg"
        os.popen(cmd % tile).readlines()

        shutil.move(os.path.join(directory, 'montage.jpg'), image_fn)
        os.chdir(_curdir)

    def _make_montage3(self, directory, image_fn, no_pictures):
        """
        Generate one big image from screnshots and optionally resize it. Uses
        PIL package to create output image.
        Arguments:
            @directory - source directory containing images
            @image_fn - destination final image
            @no_pictures - number of pictures
        timeit result:
            python /usr/lib/python2.6/timeit.py -n 1 -r 1 'from pygtktalog.video import Video; v = Video("/home/gryf/t/a.avi"); v.capture()'
            1 loops, best of 1: 18.8 sec per loop
        """
        scale = False
        row_length = 4
        if no_pictures < 8:
            row_length = 2

        if not (self.tags['width'] * row_length) > self.out_width:
            for i in [8, 6, 5]:
                if (no_pictures % i) == 0 and \
                   (i * self.tags['width']) <= self.out_width:
                    row_length = i
                    break

        coef = float(self.out_width - row_length - 1) / (self.tags['width'] * row_length)
        if coef < 1:
            dim = int(self.tags['width'] * coef), int(self.tags['height'] * coef)
        else:
            dim = int(self.tags['width']), int(self.tags['height'])

        ifn_list = os.listdir(directory)
        ifn_list.sort()
        img_list = [Image.open(os.path.join(directory, fn)).resize(dim) \
                for fn in ifn_list]

        rows = no_pictures / row_length
        cols = row_length
        isize = (cols * dim[0] + cols + 1,
                 rows * dim[1] + rows + 1)

        inew = Image.new('RGB', isize, (80, 80, 80))

        for irow in range(no_pictures * row_length):
            for icol in range(row_length):
                left = 1 + icol*(dim[0] + 1)
                right = left + dim[0]
                upper = 1 + irow * (dim[1] + 1)
                lower = upper + dim[1]
                bbox = (left, upper, right, lower)
                try:
                    img = img_list.pop(0)
                except:
                    break
                inew.paste(img, bbox)
        inew.save(image_fn, 'JPEG')

    def _make_montage(self, directory, image_fn, no_pictures):
        """
        Generate one big image from screnshots and optionally resize it. Use
        external tools from ImageMagic package to arrange and compose final
        image.

        Arguments:
            @directory - source directory containing images
            @image_fn - destination final image
            @no_pictures - number of pictures
        timeit result:
            python /usr/lib/python2.6/timeit.py -n 1 -r 1 'from pygtktalog.video import Video; v = Video("/home/gryf/t/a.avi"); v.capture()'
            1 loops, best of 1: 32.5 sec per loop
        """
        scale = False
        row_length = 4
        if no_pictures < 8:
            row_length = 2

        if (self.tags['width'] * row_length) > self.out_width:
            scale = True
        else:
            for i in [8, 6, 5]:
                if (no_pictures % i) == 0 and \
                   (i * self.tags['width']) <= self.out_width:
                    row_length = i
                    break

        tile = "%dx%d" % (row_length, no_pictures / row_length)

        _curdir = os.path.abspath(os.path.curdir)
        os.chdir(directory)

        # composite pictures
        # readlines trick will make to wait for process end
        cmd = "montage -tile %s -geometry +2+2 picture_*.jpg montage.jpg"
        os.popen(cmd % tile).readlines()

        # scale it to minimum 'modern' width: 1024
        if scale:
            cmd = "convert -scale %s montage.jpg montage_scaled.jpg"
            os.popen(cmd % self.out_width).readlines()
            shutil.move(os.path.join(directory, 'montage_scaled.jpg'),
                        image_fn)
        else:
            shutil.move(os.path.join(directory, 'montage.jpg'),
                        image_fn)

        os.chdir(_curdir)

    def _return_lower(self, chain):
        """
        Return lowercase version of provided string argument
        Arguments:
            @chain string to be lowered
        Returns:
            @string with lowered string
        """
        return str(chain).lower()

    def __str__(self):
        str_out = ''
        for key in self.tags:
            str_out += "%20s: %s\n" % (key, self.tags[key])
        return str_out

