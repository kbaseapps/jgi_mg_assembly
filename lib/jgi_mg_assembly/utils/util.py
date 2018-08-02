"""
Just some useful general utility functions.
"""
from __future__ import print_function
import os
import errno


def mkdir(path):
    """
    Safely runs the linux command mkdir on a path.
    If that path exists, just return silently instead of raising an exception.
    """
    if not path:
        raise ValueError("A path is required")
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass  # it already exists, just return
        else:
            raise  # maybe permission error, maybe something else.

def file_to_log(path):
    """
    Dumps a text file, line by line, to the app runtime log (stdout).
    """
    if not os.path.exists(path):
        raise ValueError("File path does not exist, cannot write it to standard out: {}".format(path))
    with open(path, 'r') as infile:
        print(infile.read(), end="")