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


def cprint(txt, color):
    color_map = {"black": BLACK,
                 "red": RED,
                 "green": GREEN,
                 "yellow": YELLOW,
                 "blue": BLUE,
                 "magenta": MAGENTA,
                 "cyan": CYAN,
                 "white": WHITE}
    print(COLOR_SEQ % (30 + color_map[color]) + txt + RESET_SEQ)


class DummyFormater(logging.Formatter):
    """Just don't output anything"""
    def format(self, record):
        return ""


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


log_obj = None


def get_logger(module_name, level='INFO', to_file=True, to_console=True):
    """
    Prepare and return log object. Standard formatting is used for all logs.
    Arguments:
        @module_name - String name for Logger object.
        @level - Log level (as string), one of DEBUG, INFO, WARN, ERROR and
                 CRITICAL.
        @to_file - If True, additionally stores full log in file inside
                   .pycatalog config directory and to stderr, otherwise log
                   is only redirected to stderr.
    Returns: object of logging.Logger class
    """

    path = os.path.join(os.path.expanduser("~"), ".pycatalog", "app.log")

    log = logging.getLogger(module_name)
    log.setLevel(LEVEL[level])

    if to_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_formatter = ColoredFormatter("%(filename)s:%(lineno)s - "
                                             "%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)

        log.addHandler(console_handler)

    elif to_file:
        file_handler = logging.FileHandler(path)
        file_formatter = logging.Formatter("%(asctime)s %(levelname)6s "
                                           "%(filename)s: %(lineno)s - "
                                           "%(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(LEVEL[level])
        log.addHandler(file_handler)
    else:
        devnull = open(os.devnull, "w")
        dummy_handler = logging.StreamHandler(devnull)
        dummy_formatter = DummyFormater("")
        dummy_handler.setFormatter(dummy_formatter)
        log.addHandler(dummy_handler)

    return log
