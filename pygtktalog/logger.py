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

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the
# foreground with 30

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD",
                                                               BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {'WARNING': YELLOW,
          'INFO': GREEN,
          'DEBUG': BLUE,
          'CRITICAL': WHITE,
          'ERROR': RED}

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) \
                    + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)
LEVEL = {'DEBUG': logging.DEBUG,
         'INFO': logging.INFO,
         'WARN': logging.WARN,
         'ERROR': logging.ERROR,
         'CRITICAL': logging.CRITICAL}

#def get_logger(module_name, level=None, to_file=True):
def get_logger(module_name, level=None, to_file=False):
    """
    Prepare and return log object. Standard formatting is used for all logs.
    Arguments:
        @module_name - String name for Logger object.
        @level - Log level (as string), one of DEBUG, INFO, WARN, ERROR and
                 CRITICAL.
        @to_file - If True, stores log in file inside .pygtktalog config
                   directory, otherwise log is redirected to stderr.
    Returns: object of logging.Logger class
    """

    path = os.path.join(os.path.expanduser("~"), ".pygtktalog", "app.log")
    path = "/dev/null"
    log = logging.getLogger(module_name)

    if not level:
        #log.setLevel(LEVEL['WARN'])
        log.setLevel(LEVEL['DEBUG'])
    else:
        log.setLevel(LEVEL[level])

    if to_file:
        log_handler = logging.FileHandler(path)
        formatter = logging.Formatter("%(asctime)s %(filename)s:%(lineno)s - "
                                      "%(levelname)s - %(message)s")
    else:
        log_handler = logging.StreamHandler(sys.stderr)
        formatter = ColoredFormatter("%(filename)s:%(lineno)s - "
                                      "%(levelname)s - %(message)s")

    log_handler.setFormatter(formatter)
    log.addHandler(log_handler)
    return log

