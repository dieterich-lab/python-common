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
        return _findLinks_python(dir)
    
    elif "py" in str(use).lower(): 
        return _findLinks_python(dir)
        
    elif "os" in str(use).lower(): 
        return _findLinks_os(dir)

def readLineGroup(file, N = 1, open_as = "a"):
    """
    :NAME:
        readLineGroup(file, [N = 1])
    
    :DESCRIPTION:
        Reads a file in groups of lines for parsing.
         
    :USAGE:
        readLineGroup(file, [N = 1, open_as = "r"])
        
        file: The name fo the file to be opened. 
        
        N:    The number of lines to read as a group.
              DEFAULT = 1
        
        open_as: 
              How to open the file for reading Any of the Python supported 
              read types are supported, however writing is not allowed (even
              if opened with "w+".
              
    :RETURNS:
        Yields the read lines as a list.
        
    """
    from itertools import zip_longest
    
    def grouper(iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)
            
#     N = 7 # Number of lines to read
    if isinstance(file, (list, tuple)):
        for lines in grouper(file, N, ''):
            assert len(lines) == N
            yield lines
    else:
        try:
            with open(file) as f:
                for lines in grouper(f, N, ''):
                    assert len(lines) == N
                    yield lines
        except Exception as e:
            err = "readLineGroup: Unknown error opening file '{F}' (ERR: {E})".format(F = str(file), E = str(e))
            raise RuntimeError(err)
                
def _findLinks_python(dir):
    """"""
    result = []
    for name in os.listdir(dir):
        if name not in (os.curdir, os.pardir):
            full = os.path.join(dir, name)
            if os.path.islink(full):
#                 result.append((full, os.readlink(full)))
                yield full, os.readlink(full)
    
    return result 

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
#     for i,j in _findLinks_os("//Users/mikes/Documents/tmp"):
#         print (i, ":", j)
#     f = "/etc/hosts"
    f = ["line1", "line2", "line3", "line4",]
    for l in readLineGroup(f, N = 2):
        print("===")
        print(l)
        for i in l: print(i)  
    
    