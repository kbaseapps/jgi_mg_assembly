"""
Just some useful general utility functions.
"""

import os
import errno


def mkdir(path):
    if not path:
        raise ValueError("A path is required")
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass  # it already exists, just return
        else:
            raise  # maybe permission error, maybe something else.
