##############################################################################
# Removal of the "__license__" line or content from  "__license__", or removal
# of "__author__" in this or any constituent # component or file constitutes a
# violation of the licensing and copyright agreement.
__author__      = "Mike Rightmire"
__copyright__   = "BioCom Software"
__license__     = "PERPETUAL_AND_UNLIMITED_LICENSING_TO_THE_CLIENT"
__version__     = "0.9.2.0"
__maintainer__  = "Mike Rightmire"
__email__       = "Mike.Rightmire@BiocomSoftware.com"
__status__      = "Development"
""""""
from common.checks import Checks
checks = Checks()
from common.loghandler import log

import re
import subprocess
import unicodedata

def RunSubprocess(command, *args, **kwargs):
    """
    :NAME:
        RunSubprocess(command, [output, verbose, shell, ignore])
        
    :DESCRIPTION:
        RunSubprocess is a more robust wrapper for the Python 
        subprocess.Popen command, that manages output and sanitization.
        
        Output is returned, as well as sentto any existing common.log 
        singletons. 
        
        Sanity of the command is checked, using the common.Checks
        sanity functions. 
        
    :PARAMETERS:
        command: A list of strings which are assembled into the 
                 OS-level command to be run. 
                 See subprocess.Popen for details. 
                 
        output : The object type of the output returned. 
                 Available Options: string (str) or list 
                 (DEFAULT: string). 
                
        verbose: (True/False) If True, each line from stdout is logged.
                 (DEFAULT: False)
        
        shell  : Directly passed to the "shell" parameter in the 
                 subprocess Popen.
                 (DEFAULT: False)
        
        ignore : (True/False) If True, any warnings or errors (including
                 a failure to pass the sanitization check) as ignored. 
                 (DEFAULT: False)
        
    :RETURNS:
        A string or list (see output), containing the stdout from the 
        Popen command.
    
    :USAGE:
        from common.runsubprocess import RunSubprocess
        command = [ "ls", "-la"]
        result  = RUN(command)
        print(result)
        
        [OUTPUT]
        results= total 280
        drwxrwxrwx  12 mikes  staff    384 May 15 16:25 .
        drwxr-xr-x   4 mikes  staff    128 May 15 16:25 ..
        -rw-r--r--@  1 mikes  staff   6148 May 15 16:25 .DS_Store
        -rw-r--r--   1 mikes  staff      0 Mar 14 12:54 __init__.py
        drwxr-xr-x   7 mikes  staff    224 May 16 15:38 __pycache__
        -rwxrwxrwx   1 mikes  staff   2469 May 16 15:37 file1.py

    """
    output  = str(kwargs.get('output', "str"))
    verbose = True if kwargs.get('verbose', False) else False
    shell   = True if kwargs.get('shell', False) else False
    ignore = True if kwargs.get('ignore', False) else False

    if (not ignore) and (not checks.checkSanitized(command)):
        err = ''.join(["RunSubprocess: The command list '", str(command), "' does not pass a sanitization check. !!MAY HAVE DANGEROUS CONTENT!! ABORTING."])
        raise ValueError(err)

    result = ""
    
    if verbose: log.debug("RunSubprocess: " + str(command))

    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell)

    while True:
        _stdout = p.stdout.readline()
        # If no _stdout, we're done...break out of the 'while True:' 
        if not _stdout: break
        # Store the output
        else:
            # Strip all the weird control chars
            _stdout = "".join(ch for ch in str(_stdout,'utf-8') if unicodedata.category(ch)[0]!="C")
            if len(_stdout) > 0: result += (_stdout + "\n")
            if verbose is True and len(_stdout) > 1: log.debug("RunSubprocess:" + str(_stdout))
    
    if "str"  in output.lower(): return result # Str is default
    if "list" in output.lower(): return result.split() 

if __name__ == '__main__':
#     log.debug("__main__", logfile = 'syslog', app_name = "Protein_LFQ_Seg1", log_level = 10, screendump = True)
    command =["ls", "'-la", "/"
#               "find", "/usr/", "-iname",  "'*.py'",  
#                 "|", "grep", "-i", "'python'", "|", "grep", "-i", "'2.7'"
                ]
    result = RunSubprocess(command, shell = True)
    print(type(result))
    print(result)
    l = result.split()
    print (l)
    



