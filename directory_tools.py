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
import unicodedata


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

def readLineGroup(file, N = 1, open_as = "r"):
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

    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    while True:
        _stdout = p.stdout.readline()
        # If no _stdout, we're done...break out of the 'while True:' 
        if not _stdout: break
        # Store the output
        else:
            # Strip all the weird control chars
            line = "".join(ch for ch in str(_stdout,'utf-8') if unicodedata.category(ch)[0]!="C")
            line = line.split("/", 1)[1]
            line = line.split(" -> ", 1)
            _result = ()
            if len(line) < 1:
                print("Find response does not show the original file NOR the linked file. This should never happen. !PLEASE EXAMINE OUTPUT!")
                line = [None,None]
            elif len(line) == 1:
                print("Find response does not show the linked file. !Returning None for linked file.!")
                line.append(None) 
            yield line[0], line[1]


if __name__ == '__main__':
    for i,j in _findLinks_os("/mnt/ARCHIVEDISKS/archive_disk_3_contents/"):
        print (i, ":", j)
    f = "/etc/hosts"
    #===========================================================================
    # f = ["line1", "line2", "line3", "line4",]
    # for l in readLineGroup(f, N = 2):
    #     print("===")
    #     print(l)
    #     for i in l: print(i)  
    #===========================================================================
    
    
