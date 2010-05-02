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
        formatter = logging.Formatter("%(asctime)s %(filename)s:%(lineno) - "
                                      "%(name)s - %(levelname)s - "
                                      "%(message)s")
    else:
        log_handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter("%(name)s - %(filename)s:%(lineno)s - "
                                      "%(levelname)s - %(message)s")

    log_handler.setFormatter(formatter)
    log.addHandler(log_handler)
    return log
