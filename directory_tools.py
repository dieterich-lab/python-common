#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__      = "Mike Rightmire"
__copyright__   = "Universitäts Klinikum Heidelberg, Section of Bioinformatics and Systems Cardiology"
__license__     = "Not licensed for private use."
__version__     = "0.9.0.0"
__maintainer__  = "Mike Rightmire"
__email__       = "Michael.Rightmire@uni-heidelberg.de"
__status__      = "Development"

from common.checks import Checks
checks = Checks()
_delim = checks.directory_deliminator()

import os

def findLinks(dir):
    """
    :NAME:
        findLinks(dir)

    :DESCRIPTION:
        Searches a directory and iterates tuples as (path, linked_oath)
        
    :PARAMETERS:
        dir: (Mandatory) The FULL PATH to the starting directory to search for 
             links. No default.
             
    :RETURNS:
        Yields as an iterator tuples of (path, linked_path)
        
    """
    for name in os.listdir(dir):
        if name not in (os.curdir, os.pardir):
            full = os.path.join(dir, name)
            if os.path.islink(full):
                yield full, os.readlink(full)
