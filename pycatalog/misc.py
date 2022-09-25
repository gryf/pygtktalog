"""
    Project: pyGTKtalog
    Description: Misc functions used more than once in src
    Type: lib
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-04-05
"""
import os
import sys

from pycatalog import logger

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)

RESET_SEQ = '\033[0m'
COLOR_SEQ = '\033[1;%dm'
BOLD_SEQ = '\033[1m'

LOG = logger.get_logger()


def colorize(txt, color):
    """Pretty print with colors to console."""
    color_map = {'black': BLACK,
                 'red': RED,
                 'green': GREEN,
                 'yellow': YELLOW,
                 'blue': BLUE,
                 'magenta': MAGENTA,
                 'cyan': CYAN,
                 'white': WHITE}
    return COLOR_SEQ % color_map[color] + txt + RESET_SEQ


def float_to_string(float_length):
    """
    Parse float digit into time string
    Arguments:
        @number - digit to be converted into time.
    Returns HH:MM:SS formatted string
    """
    hour = int(float_length / 3600)
    float_length -= hour*3600
    minutes = int(float_length / 60)
    float_length -= minutes * 60
    sec = int(float_length)
    return f"{hour:02}:{minutes:02}:{sec:02}"


def asserdb(func):
    def wrapper(args):
        if not os.path.exists(args.db):
            print(colorize("File `%s' does not exists!" % args.db, 'red'))
            sys.exit(1)
        func(args)
    return wrapper
