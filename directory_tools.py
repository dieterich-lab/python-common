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
# from common.runsubprocess import RunSubprocess

import os
import subprocess

def findLinks(dir, use = "default"):
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
    if   "default" in str(use).lower(): 
        yield _findLinks_python(dir)
    
    elif "py" in str(use).lower(): 
        yield _findLinks_python(dir)
        
    elif "os" in str(use).lower(): 
        yield _findLinks_os(dir)

def _findLinks_python(dir):
    """"""    
    for name in os.listdir(dir):
        if name not in (os.curdir, os.pardir):
            full = os.path.join(dir, name)
            if os.path.islink(full):
                yield full, os.readlink(full)

def _findLinks_os(dir):
    if   checks.checkOS('nix'):
        _dir = str(dir)
        # remove anything after a ";" for sanity
        _dir = _dir.split(";")[0]
        command = ' '.join(["find", _dir, "-type", "l", "-exec", "ls", "-la", "{}", "\\;"])
#         print(command)
        stdoutdata = subprocess.getoutput(command)
#         print(stdoutdata)
        stdoutdata = stdoutdata.split("\n")
#         print(stdoutdata)
        for line in stdoutdata:
#             print(line)
            line = line.split("/", 1)[1]
#             print(line)
            line = line.split(" -> ", 1)
#             print(line)
            yield line[0], line[1]
    
    
    elif checks.checkOS('win'):
        err = "findLinks: Windows is not yet supported."
        raise NotImplementedError(err) 
   
    else:
        err = "findLinks: OS '{O}' is not yet supported.".format(O = checks.checkOS())
        raise NotImplementedError(err) 

if __name__ == '__main__':
    for i,j in _findLinks_os("//Users/mikes/Documents/tmp"):
        print (i, ":", j)