"""
    Project: pyGTKtalog
    Description: Logging functionality
    Type: core
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-09-02
"""
import os
import sys
import logging

LEVEL = {'DEBUG': logging.DEBUG,
         'INFO': logging.INFO,
         'WARN': logging.WARN,
         'ERROR': logging.ERROR,
         'CRITICAL': logging.CRITICAL}

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {'WARNING': YELLOW,
          'INFO': GREEN,
          'DEBUG': BLUE,
          'CRITICAL': WHITE,
          'ERROR': RED}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) \
                    + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


#def get_logger(module_name, level='INFO', to_file=False):
def get_logger(module_name, level='DEBUG', to_file=True):
#def get_logger(module_name, level='INFO', to_file=True):
#def get_logger(module_name, level='DEBUG', to_file=False):
    """
    Prepare and return log object. Standard formatting is used for all logs.
    Arguments:
        @module_name - String name for Logger object.
        @level - Log level (as string), one of DEBUG, INFO, WARN, ERROR and
                 CRITICAL.
        @to_file - If True, additionally stores full log in file inside
                   .pygtktalog config directory and to stderr, otherwise log
                   is only redirected to stderr.
    Returns: object of logging.Logger class
    """

    path = os.path.join(os.path.expanduser("~"), ".pygtktalog", "app.log")
    #path = "/dev/null"
    log = logging.getLogger(module_name)
    log.setLevel(LEVEL[level])

    console_handler = logging.StreamHandler(sys.stderr)
    console_formatter = ColoredFormatter("%(filename)s:%(lineno)s - "
                                  "%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    log.addHandler(console_handler)

    if to_file:
        file_handler = logging.FileHandler(path)
        file_formatter = logging.Formatter("%(asctime)s %(levelname)6s "
                                           "%(filename)s: %(lineno)s - "
                                           "%(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(LEVEL[level])
        log.addHandler(file_handler)

    return log
