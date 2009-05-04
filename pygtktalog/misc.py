"""
    Project: pyGTKtalog
    Description: Misc functions used more than once in src
    Type: lib
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-04-05
"""

def float_to_string(float_length):
    """
    Parse float digit into time string
    Arguments:
        @number - digit to be converted into time.
    Returns HH:MM:SS formatted string
    """
    hour = int(float_length / 3600);
    float_length -= hour*3600
    minutes = int(float_length / 60)
    float_length -= minutes * 60
    sec = int(float_length)
    return "%02d:%02d:%02d" % (hour, minutes, sec)

