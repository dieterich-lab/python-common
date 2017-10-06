##############################################################################
# Removal of the "__license__" line or content from  "__license__", or removal
# of "__author__" in this or any constituent # component or file constitutes a
# violation of the licensing and copyright agreement.
__author__      = "Mike Rightmire"
__copyright__   = "BioCom Software"
__license__     = "PERPETUAL_AND_UNLIMITED_LICENSING_TO_THE_CLIENT"
__version__     = "0.9.1.0"
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
    """
    verbose = kwargs.pop('verbose',False)
#     output  = kwargs.pop('output', "string") # Depricated
    shell   = kwargs.pop('shell', False)
    if shell: shell = True # Ensure is boolean
    
    if not checks.checkSanitized(command):
        err = ''.join(["RunSubprocess: The command list '", str(command), "' does not pass a sanitization check. !!MAY HAVE DANGEROUS CONTENT!! ABORTING."])
        raise ValueError(err)

    result = ""
    
    #=== DEPRICATED ============================================================
    # if   isinstance(output,list):
    #     err  
    #     result = output
    # elif isinstance(output,str): 
    #     if re.match('^\s*st.*$', str(output), re.IGNORECASE):       result = str()
    #     elif re.match('^\s*te?x?.*$', str(output), re.IGNORECASE):  result = str()
    #     elif re.match('^\s*li?s?t?.*$', str(output), re.IGNORECASE):result = []

    # if result is False: 
    #    err = ''.join(["BiocomCommon.RunSubprocess: ", "Unable to determine output type. ", "Parameter 'output' must be a Python object of 'str()' or 'list()' or the text 'string' or 'list'. "])
    #    raise ValueError(err)
    #===========================================================================
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell)
    log.debug("RunSubprocess: " + str(command))

    while True:
        _stdout = p.stdout.readline()
        # If no _stdout, we're done...break out of the 'while True:' 
        if not _stdout: break
        # Store the output
        else:
            # Strip all the weird control chars
            _stdout = "".join(ch for ch in unicode(_stdout) if unicodedata.category(ch)[0]!="C")
            if len(_stdout) > 0: result += (_stdout + "\n")
            #=== DEPRICATED ====================================================
            # elif isinstance(result, list) and len(_stdout) > 0: result.append(_stdout)  
            #===================================================================
            if verbose is True and len(_stdout) > 1: log.debug("RunSubprocess:" + str(_stdout))

    return result

if __name__ == '__main__':
    log.debug("__main__", logfile = 'syslog', app_name = "Protein_LFQ_Seg1", log_level = 10, screendump = True)
    command =["ls", "'-la", "/"
#               "find", "/usr/", "-iname",  "'*.py'",  
#                 "|", "grep", "-i", "'python'", "|", "grep", "-i", "'2.7'"
                ]
    result = RunSubprocess(command, shell = True)
    print 'result=', result #3333




