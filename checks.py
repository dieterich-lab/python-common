#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################################################
# Removal of the "__license__" line or content from  "__license__", or removal 
# of "__author__" in this or any constituent # component or file constitutes a 
# violation of the licensing and copyright agreement. 
__author__      = "Mike Rightmire"
__copyright__   = "BioCom Software"
__license__     = "PERPETUAL_AND_UNLIMITED_LICENSING_TO_THE_CLIENT"
__version__     = "0.9.1.7"
__maintainer__  = "Mike Rightmire"
__email__       = "Mike.Rightmire@BiocomSoftware.com"
__status__      = "Development"
##############################################################################

from math import ceil
# from urlparse import urlparse
from os import getcwd

import inspect
import ntpath
import os.path
import pickle
import re
import subprocess
import sys
import tempfile

global linux_blacklist
# These are regex strings
# Think about spaces here
linux_blacklist = [
                   'sudo',
                   'su',
                   'bash',
                   'rm -{0,1}[RrFf]*', # remove
                   'chmod', # Permissions
                   'chown', # Ownership
                   'kill',
                    'rm', 
                    'mkfs', 
                    'dd', 
                    'fork', 
                    'while', 
                    'tar', 
                    'wget', 
                    'sh', 
                    '?sh', 
                    'python',
                    'perl',
                    'chmod', 
                    'chown', 
                    '__attribute__', 
                    ';', # ALWAYS PUT ME LAST 
                   ]

global windows_blacklist
windows_blacklist = []

def _dir_delim():
    """
    Just a pointer to directory_deliminator()
    """
    if _checkOS("windows"): 
        return "\\"
    else: 
        return "/"
                  

def _makefile(path):
    """"""
    _path = str(path)
    # Set starter error message
    err = "checks._makefile:"
#     err = ''.join(["checks._makefile: '_path' of ", str(_path), " "]) 
    # Check if it looks liek a file
    if len(_path) < 1 or _path.endswith(_dir_delim()) :
        return False
    
    _dir = ntpath.dirname(_path) + _dir_delim()
    _file = ntpath.basename(_path)
    
#         err = ''.join([err, "Does not appear to be a valid full path with filename. "])
#         raise ValueError(err)

    # Try to make just the directory (and then try to make the file next)
    try:
        _makedir(_dir)

    except Exception as e:
        if 'exists': pass # If it exists, all is good. 
        else:
            # Failed to make. Return false
#             return False
            err = "{M}. Unable to create directory (ERR: '{E}', path:'{P}')".format(M = err, E = str(e), P = _path)
#             err = ''.join([err, "Was unable to create directory. ","(", e.message, ")."])
            raise type(e)(err)
    # Make the file itself.     
    try:
        open(_path, 'w+') # Use path not _dir or _file
        return True
    
    except Exception as e:
#         return False
        err = "{M}. Unable to create file (ERR: '{E}', path:'{P}')".format(M = err, E = str(e), P = _path)
#         err = ''.join([err, "Was unable to create file. ","(", e.message, ")."])
        raise type(e)(err)

def _makedir(_path):
    """"""
    _dir = ntpath.dirname(_path)
#     _dir = _dir + self._delim
    _dir = _dir + self.directory_deliminator()
    try:
        os.makedirs(_dir)
        return True
    
    except Exception as e:
        err = "Error attempting to create directory(ies) '{D}' (ERROR: E)".format(D = _dir, E = str(e))
#         return False
        raise type(e)(err)


def _check_for_directory_flag(**kwargs):
    if (  kwargs.pop('dir',         False) or
          kwargs.pop('directory',   False) or
          kwargs.pop('folder',      False) 
        ):
        return True
    else:
        return False
    
def _check_for_file_flag(**kwargs):
    if (  kwargs.pop('file',       False) or
          kwargs.pop('filename',   False) 
        ):
        return True
    else:
        return False
        
#===============================================================================
# def _checkSanitized(s, blacklist): # Blackist must be passed in 
#     # Check blacklist is list
#     if not isinstance(blacklist, list):
#         e = ''.join([ 'checks._checkSanitized:', "Parameter 'blacklist' must be a list, not '", str(type(blacklist)), "'. " ])
#         raise AttributeError(e)
#         
#     for word in blacklist:
#         word = str(word) # In case blacklist is passed in 
#         if re.search(word,s): return False
#     
#     return True    
#===============================================================================
    
#===============================================================================
# def _checkLinuxSanitized(s, blacklist = None):
#     """"""
#     if re.search('[;]', s): return False # ';' common command insertion
#     # Blacklist specific to linux        
#     if blacklist is None:
#         """
#         NOTE: THE POSITIONS OF THE SPACES IS CRITICAL HERE.
#         Commands are only commands if spaces before and/or after
#         Think about spaces here
#         """
#         # Think about spaces here
#         blacklist = linux_blacklist
# #         blacklist = [
# #                        ' rm ', # remove
# #                        ' -[RrFf]*', # dangerous flags. Note spaces.
# #                        ' chmod ', # Permissions
# #                        ' chown ', # Ownership
# #                        ]
#     return _checkSanitized(s, blacklist)
#===============================================================================
    
#===============================================================================
# def _checkOSXSanitized(s, blacklist = None):
#     ### osx specific checks here ###
#     return _checkLinuxSanitized(s, blacklist)
#===============================================================================

#===============================================================================
# def _checkWindowsSanitized(s, blacklist = None):
#     raise NotImplementedError()
#===============================================================================
def _checkOS(os = None):
    """
    checkOS(['os'])
    
    DESCRIPTION
        checkOS returns either the OS platform (if called with no option), 
        or a True/False if the passed option matches the OS type.
        
    OPTIONS
        os = a STRING containing the name of the os to be identified. If the 
             platform matches the 'os', checkOS will return True, 
             otherwise it returns False.
             
            Acceptable 'os' parameters are:
                windows = T if windows OS
                win     = T if windows OS
                win32   = T if windows 32 bit specifically
                win64   = T if windows 64 bit specifically
                freebsd = T if FreeBSD specifically
                gnu     = T if GNU OS specifically
                linux   = T if linux, or GNU, or FreeBAD
                unix    = T if Solaris, or riscos, or FreeBSD
                *nix    = T if linux, or GNU, or FreeBAD, or Solaris, 
                          or riscos, or FreeBSD
                risc    = T is riscos
                atheos  = T is atheos
                solaris = T if solaris, or sunos
    """
    def _windows_os():
        if sys.platform.startswith('win'): return True
        else: return False

    def _windows32_os():
        if str(sys.platform) == "win32":  return True
        return False

    def _windows64_os():
        if str(sys.platform) == "win64": return True
        return False
    
    def _linux_os():
        if sys.platform.startswith('linux'): return True
        if _gnu_os(): return True
        if _freebsd_os(): return True
#             if _osx_os(): return True
        return False
        
    def _osx_os():
        if sys.platform.startswith('darwin'): return True
        else: return False                
    
    def _cygwin_os():
        if sys.platform.startswith('cygwin'): return True
        else: return False
        
    def _os2_os():
        if sys.platform.startswith('os2'): return True
        else: return False
        
    def _os2emx_os():
        if sys.platform.startswith('os2emx'): return True
        else: return False
        
    def _riscos_os():
        if sys.platform.startswith('riscos'): return True
        else: return False
        
    def _atheos_os():
        if sys.platform.startswith('atheos'): return True
        else: return False                

    def _sun_os():
        if sys.platform.startswith('sunos'): return True
        else: return False
                
    def _freebsd_os():
        if sys.platform.startswith('freebsd'): return True
        else: return False

    def _gnu_os():
        if sys.platform.startswith('gnu'): return True
        else: return False

    def _unix_os():
        if _freebsd_os(): return True
        if _sun_os(): return True
        if _riscos_os():  return True
        return False

    def _nix_os():
        if _freebsd_os(): return True
        if _sun_os(): return True
        if _riscos_os(): return True
        if _linux_os(): return True
        if _gnu_os(): return True
        if _osx_os(): return True
        if _cygwin_os(): return True
        return False
                                                                    
    def _unknown_os():
        return sys.platform    

    _os = str(os).lower()
    
    if os is None: return sys.platform
    if sys.platform == _os: return True
            
    return {
            "win"       :_windows_os,
            "w"         :_windows_os,
            "windows"   :_windows_os,

            "win32"     :_windows32_os,
            "w32"       :_windows32_os,
            "x32"       :_windows32_os,

            "windows32" :_windows32_os,
            "win64"     :_windows64_os,
            "w64"       :_windows64_os,
            "x64"       :_windows64_os,
            "ia64"      :_windows64_os,
            "windows64" :_windows64_os,
             
            "g"         :_gnu_os, 
            "gnu"       :_gnu_os,

            "lin"       :_linux_os, 
            "l"         :_linux_os,
            "linux"     :_linux_os,
            "linux2"    :_linux_os,
            
            "freebsd"   :_freebsd_os,
            "free"      :_freebsd_os,
            "bsd"       :_freebsd_os,
            
            "mac"       :_osx_os,
            "osx"       :_osx_os,
            "darwin"    :_osx_os,
            "dar"       :_osx_os,
            "apple"     :_osx_os, 
            
            "cygwin"    :_cygwin_os,
            "cyg"       :_cygwin_os,
            "c"         :_cygwin_os,
                      
            "os2emx"    :_os2emx_os,
            "emx"       :_os2emx_os,
                
            "os2"       :_os2_os,
                
            "risc"      :_riscos_os,
            "riscos"    :_riscos_os,
                
            "atheos"    :_atheos_os,
            "athe"      :_atheos_os,
            "ath"       :_atheos_os,        
                    
            "solaris"   :_sun_os,
            'sol'       :_sun_os,
            'sun'       :_sun_os,
                    
            'unix'      :_unix_os,
            'nix'       :_nix_os,
            '*nix'      :_nix_os,
            
            }.get(_os)()
    # Nothing matched. error basically
#         return False
    err = ''.join([self.__class__.__name__, ".", inspect.stack()[0][3], ": ", 
                   "Unable o successfully match an OS. Erroring out instead of passing a False back. "])
    raise OSError(err)

def _sanitize(value, blacklist):
    """
    :RETURN: 
    returns a tuple (True/False, String)
    
    :PARAMETERS:
    value = the string to be checked. If not sent as a string, will be converted
            to a string. 
            
    blacklist = The list of words that are invalid (should not be included in
                the string. 
                
    remove = If True, return the string with the blacklisted words removed. 
             If False, returns the original string.
             
    system = The type of OS to be checked. Only useful if no blacklist was 
             submitted. If set, AND NO BLACKLIST, the default blacklist for that 
             OS will be used.  
    """
    print("_sanitize.value = ", value) #333
    if not isinstance(blacklist, (list,tuple)):
        e = "checks._sanitize: Parameter 'blacklist' must be a list, not '{T}' (blacklist = '{B}'). ".format( T = str(type(blacklist)), B = str(blacklist))
        raise AttributeError(e)

    result = value
    for word in blacklist:
        pattern = ';*\s*{}'.format(str(word))
        result = re.sub(pattern, '', result)

    if result == value: return (True, result)
    else: return (False, result)

def _linux_sanitize(value, blacklist = None):
    # First remove anything coming after a semi-colon
    value = str(value).split(";")[0]
    if blacklist is None: blacklist = linux_blacklist
    return _sanitize(value, blacklist)

def _windows_sanitize(value, blacklist = None):
    err = ''.join("'Checks.sanitize()' is not yet implemented for a Windows environment. ")
    raise NotImplementedError(err)

def _OSX_sanitize(value, blacklist = None):
    # Basically teh same a Linux
    return _linux_sanitize(value, blacklist)
#     if blacklist is None: blacklist = linux_blacklist
#     return _sanitize(value, blacklist)

def _errout(msg, errtype = None):
    if 'exception' in str(errtype).lower():
        raise type(errtype)(msg)
    else:
        raise Exception(msg)
    
def _is(variable, variable_type):
    if 'in' in str(variable_type).lower():
        if isinstance( variable, int ):     return True
        else:                               return False

    elif 'fl' in str(variable_type).lower():
        if isinstance( variable, float ):   return True
        else:                               return False

    elif 'str' in str(variable_type).lower():
        if isinstance( variable, str ):     return True
        else:                               return False
        
    else:
        raise AttributeError("'" + str(variable_type) + "' is not a valid variable check type.")

def _fileExists(path, **kwargs):
    """"""
    # MUST be a full path
    if os.path.isfile(path): return path

def _dirExists(path, *args, **kwargs):
    create = kwargs.pop('create', False)
    error  = kwargs.pop('error', False)
    if os.path.isdir(path):
        return path
    # Does not exist
    if create:
        try:
            os.makedirs(path)
            return path
        except Exception as e:
            if error:
                err = "{C}.{M}: Unable to create path '{P}' with error '{E}'.".format(
                            C = self.__Class__.__name__,
                            P = str(path), 
                            M = inspect.stack()[0][3], 
                            E = str(e))
                raise type(e)(err)
            else:
                return False
    else:
        return False

def _windowsPathFormat(path):
    _path = str(path)
    p = r'(\s*[a-zA-Z]:[\\]*|\.*)(?![\/\?\<\>:\*\|\"])'
    try:
        m = re.match(p, _path)
        if m.groups()[0] : return True
        else             : return False
    except IndexError: 
        return False

def _linuxPathFormat(path):
    _path = str(path)
    p = r'(\s*[/\.]*)(.*)'
    try:
        m = re.match(p, _path)
        if m.groups()[0] : return True
        else             : return False
    except IndexError: 
        return False
 
def _re(p, s, type, *args, **kwargs):
    """"""
    groups      = kwargs.pop('groups', [])
    ignorecase  = kwargs.pop('ignorecase', False)
    
    # check params
    if not isinstance(p, str) or not isinstance(s, str): 
        raise ValueError(''.join(["Both parameters 'p' (pattern) and 's' (string to be searched) must be of type str(). p=(", str(type(p)), ")'", str(p), "', s=(", str(type(s)), ")'", str(s), "'. "]))
    if not isinstance(groups, (list, tuple)): 
        raise ValueError(''.join(["file_utils._check_re_search:",  "Parameter 'groups' ('", str(groups), "') must be a list of integers indicating which matched group items to return. "]))

    # match pattern(p), against string(s)
    if 'm' in str(type).lower():
        if ignorecase:  result = re.match(p,s, re.IGNORECASE)
        else:           result = re.match(p,s)
    # search
    else:
        if ignorecase:  result = re.search(p,s, re.IGNORECASE)
        else:           result = re.search(p,s)

    # If nothing found, return an empty list
    if result is None: return []
    # Returns all
    if ( (groups == []) or ('all' in str(groups).lower()) ): return result.groups()  
    # Else return specific groups
    else:
        list_result = []
        for num in groups:
            try: 
                num = int(num)
                list_result.append(result.group(num))
            except ValueError as e:  raise ValueError(groups_err + '(' + str(e) + ').')
            # Ignore invalid groups indexes
            except IndexError as e:
                pass
#                 msg = ''.join(["Parameter 'groups' index number of '", str(num), "' is not valid [no results.group(", str(num), ") exists]. Skipping. "])
#                 log.warning(msg)
        # Done
        return list_result

def pause(msg = "Press 'Enter' to continue...", dump = False):
    import time
    try: 
        t = float(msg) # Is a number or num string
        if dump: print("Sleeping for {T} seconds...".format(T = str(t)))
        time.sleep(t)
    
    except ValueError: # Assumes interactive response
        input(msg)
 
class Checks(object):
    def __init__(self):
        self._calling_path = os.path.dirname(inspect.getfile(sys._getframe(1)))
        self._calling_file = str(inspect.getfile(sys._getframe(1)))
        self._delim = self.directory_deliminator()
        
    def directory_delimiter(self):
        """
        Just a pointer to directory_deliminator()
        """
        return _dir_delim()
                      
    def directory_deliminator(self):
        """
        Just a pointer to directory_deliminator()
        """
        return _dir_delim()
                      
    def obfuscate_key(self, _key):
        _key = str(_key)
    
        if len(_key) < 5: return (len(_key) * '*')
        
        _buffer = int(ceil(len(_key) * .2))
        if _buffer > 3: _buffer = 3
    
        _obbedkey = ''.join([
                             _key[:_buffer], 
                             ((len(_key)-(_buffer*2)) * "*"), 
                             _key[len(_key) - (_buffer):]
                             ])
        return _obbedkey
                      
    #===Depricated==============================================================
    # def checkInt(self, variable):
    #     return _is(variable, variable_type = 'int')
    # checkInteger = checkInt
    #                   
    # def checkFloat(self, variable):
    #     return _is(variable, variable_type = 'fl')
    # checkDecimal = checkDec = checkFloat
    #                   
    # def checkStr(self, variable):
    #     return _is(variable, variable_type = 'str')
    # checkString = checkStr
    #===========================================================================
                      
    def check(self, type, line, *args, **kwargs):
         
        if re.match("^.*path.*$", str(line).lower()):
            fullPathCheck(line) 

    def findExecutablePath(self, exename, expected_path = None, search = True, *args, **kwargs):
            # Linux/OSX try first
            try:
                p = subprocess.Popen(['which', exename],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _path = p.communicate()[0] # take first component
                if len(_path) > 0:
                    return  ntpath.dirname(_path) + self.directory_delimiter()
                # which did not find.
                if expected_path is not None:
                    p = subprocess.Popen(['ls', expected_path + '\\' + exename],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    _path = p.communicate()[0] # take first component
                    if exename in str(_path):
                        return expected_path
                # ls did not find the exe or no directory at all (wont error)
                if search is True:
                    p = subprocess.Popen(['find', '/','-name',exename],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    _path = p.communicate()[0] # take first component
                if len(_path) > 0:
                    return  ntpath.dirname(_path) + self.directory_delimiter()
                # Never found anything, return None and assume caller will error
                return None
            # If here, one of the commands given to popen was invalid.
            # We will just pass and try again from the assumption it is a windows system. 
            # We can add extra OS here if needed.  
            except (OSError) as e: pass
            
            # Windows
            try:
                p = subprocess.Popen(['where', exename],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _path = p.communicate()[0] # take first component
                if len(_path) > 0: return  ntpath.dirname(_path) + self.directory_delimiter()
                # where did not find. 
                if expected_path is not None:
                    p = subprocess.Popen(['dir', expected_path + '/' + exename],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    _path = p.communicate()[0] # take first component
                    if exename in str(_path): return expected_path
                # search the system (FUTURE)
                # Something like 
                #===============================================================
                # @echo off & setLocal EnableDELAYedeXpansion
                # 
                # for %%d in (c d e f g h i j k l m n o p q r s t u v w x y z) do (
                #   if exist %%d: (
                #       for /f "tokens=* delims= " %%a in ('dir/b/s %%d:\basecontent.7z 2^>nul') do (
                #         7za.exe x "%%a"
                #       )
                #   )
                # )
                #===============================================================
                
            except WindowsError as e: pass
            
            # Try a different OS here. 
            
            # FINALLY 
            return None
    
    def fullPath(self, path, *args, **kwargs):
        _path = str(path).strip() # REMOVE WHITESPACE FROM ENDS
        
        if not _path.startswith(self._delim):
            # Its relative or just a single word (assuming relative)
            _path = ''.join([ntpath.dirname(self._calling_file), self._delim, _path])
        
        return _path
                      
    def fullPathCheck(self, path, *args, **kwargs):
        """
        INCOMPLETE
        """
        path = str(path)
#         self._delim = self.directory_deliminator()
        if path.endswith(self._delim): _endslash = True
        else:                     _endslash = False
        if (not self.isPathFormat(path, full = True, relative = False, trailing = _endslash)): return False

        return True
    #===============================================================================
    # def checkWindowsPathFormat(_path, endslash = False):
    #     _path = str(_path)
    # 
    #     wp = re.compile("^(([a-zA-Z]:\\\)|(\.\\\)|(\.\.\\\)).*$")
    # 
    #     if not re.match(wp, _path): return False
    # 
    #     if endslash:
    #         if _path[-1:] == "\\": return True
    #         else: return False
    #     
    # def checkLinuxPathFormat(_path, endslash = False):
    #     _path = str(_path)
    #     
    #     lp = re.compile("^((\./)|(\.\./)|(/)).*$")
    # 
    #     if not re.match(lp, _path): return False
    #     
    #     #Must come after re.match
    #     if endslash:
    #         if _path[-1:] == "/": return True
    #         else: return False
    #===============================================================================
    
    #===============================================================================
    # def checkPathFormat(path, full = False, relative = False, trailing = False):
    #     return isPathFormat(path, full = False, relative = False, trailing = False)
    # #     _path = str(_path)
    # #     if   checkWindowsPathFormat(_path, endslash): return True
    # #     elif checkLinuxPathFormat(_path, endslash)  : return True
    # #     else: return False
    #===============================================================================
        
    def pathExists(self, path, **kwargs): #create = False, full = True, relative = False, trailing = False, **kwargs):
        """
        Check that a full path exists when ONLY the full path is path
        
        This differs from directoryExists, which checks (ONLY) that the full path 
        exists when path is the full path PLUS THE FILENAME. 
        """
        _calling_path = os.path.dirname(inspect.getfile(sys._getframe(1)))
        _calling_file = str(inspect.getfile(sys._getframe(1)))
        _path = str(path).strip() # Remove whitespaces
#         _delim = self.directory_deliminator()
        _result = False # Negative assumption
        _dir =  _check_for_directory_flag(**kwargs)
        _file = _check_for_file_flag(**kwargs)
        _create = kwargs.pop('create', False)
        #Check if relative, make full if it is. Use the calling files path
        _path = self.fullPath(path)
        # At this point, we should have a full path in one form
        # Check for both a dir and a file. If neither return False
        
        #=======================================================================
        # print('At os.path.exists...'
        # print("_path =", _path #333
        # print("_file =", _file #3333
        # print("_dir = ", _dir #333
        #=======================================================================
        
        _expanded_path = os.path.expanduser(_path) # Fixes spaces in dir problem
        if os.path.exists(_expanded_path): # path exists as either file or dir
#         if os.path.exists(_path): # path exists as either file or dir
            if _file  : return _fileExists(_path) # Check specifically file
            elif _dir : return _dirExists(_path) # Check specifically dir
            else      : return _expanded_path

        else: # Does not exists, cheack for create
            if _create: # Default False
                if _dir     : 
                    try:
                        if _makedir(_path): return _path
                    except Exception as e:
                        err = "Checks.pathExists.create: Unable to create directory '{P}'. (ERR: {E}).".format(P = str(_path), E = str(e))
                        raise RuntimeError(err)
                elif _file  :
                    try: 
                        if _makefile(_path): return _path
                    except Exception as e:
                        err = "Checks.pathExists.create: Unable to create file '{P}'. (ERR: {E}).".format(P = str(_path), E = str(e))
                        raise RuntimeError(err)
                        
                else        :
                    err = ''.join(["Checks.pathExists.create: ", "The 'create' param muct be accompanied by a 'directory = True' or 'file = True' flag. "])
                    raise ValueError(err)
        
            else: # Create = False, return False
                return False
                      
    def fullPathExists(self, path, **kwargs): #create = False, full = True, relative = False, trailing = False):
        return self.pathExists(path, **kwargs)
                
    def pathType(self, path):
        # Local file system
        # ntpath will check for local absolute paths
        if   ntpath.isabs(path): return "local"
        elif re.match("^\s*[.]{1,2}" + self._delim + ".*$", path): return 'local'
        # AMAZON S3
        elif re.match("^\s*s3://.*$", path, re.IGNORECASE): return "s3"
        # web
        elif re.match("^\s*http://.*$", path,  re.IGNORECASE): return "http"
        elif re.match("^\s*https://.*$", path,  re.IGNORECASE): return "https"
        # elif more 
        else:
            return 'unknown'
                      
    def fileExists(self, file, *args, **kwargs):
        """
        :NAME:
            fileExists(file, [*args, **kwargs])
        
        :PARAMETERS:
            file:   Path and filename
            
            create: If True, create a blank file by filename
            
        :DESCRIPTION:
            Returns True if file exists
            
            If file does not exist but 'create' is True, will attempt to create 
            a blank file at /path/name
            
            Otherwise retruns False
        """
        _file = str(file)
        if _fileExists(_file):            return True
        elif kwargs.pop('create', False): return _makefile(_file) 
        else:                             return False
    isFile = fileExists

    def directoryExists(self, directory, *args, **kwargs):
        """
        :NAME:
            directoryExists(directory, [*args, **kwargs])
        
        :PARAMETERS:
            directory:   Path and filename
            
            create: If True, create a blank directory by said name
            
        :DESCRIPTION:
            Returns True if directory exists
            
            If directory does not exist but 'create' is True, will attempt to create 
            a blank directory at /path/name
            
            Otherwise returns False
        """
        _directory = str(directory)
        if _dirExists(_directory):            return True
        elif kwargs.pop('create', False): return _makedir(_directory) 
        else:                             return False
    isdirectory = isDir = directoryExists

    def checkServername(self, _name):
        if len(_name) < 1: return False
        if re.match("^[a-zA-Z0-9-]*$", str(_name)): return True
        if checkIP(_name): return True
        else: return False
                      
    def checkIP(self, IP):
        """"""
        IP = str(IP)
        IP = IP.lstrip()
        IP = IP.rstrip()
        
        pattern = (''.join([ "^", "(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})" "$"]))
        pattern = re.compile(pattern, re.IGNORECASE)
    
        if pattern.match(IP):   return True
        else:                   return False
                      
    def checkURI(self, URL = None, URI = None, *args, **kwargs):
        """
        :NAME:
            checkURI(URL = STRING/None, URI = STRING/None [, *args, **kwargs])
        
        :DESCRIPTION:
            Returns True or False if string is a validly formatted URL/URI
        
        :PARAMETERS:
            URL: (String) A URL in the format:
                 http://www.google.com/somewhere
                
            URI: (String) A URI in the format:
                 <scheme>://main/sub
                 s3://dev.myserver.com/dir/dir/file.ext
        
        :USAGE:
            import Checks
            checks = Checks()
            if checks.checkURI('s3://dev.myserver.com/dir/dir/file.ext'):
                print('It is Valid'
            else:
                print('It is invalid'
        """
        if URL is None: 
            if URI is None:
                return False
            else:
                URL = URI
                
        URL = str(URL)
        URL = URL.strip()
        #=======================================================================
        # pattern = ("^(https?){0,1}"        +               # http/https
        #             "(://){0,1}"            +               # ://
        #             "(\w+\.){0,}" +                  # Prefix [I.e. www.] (Optional)
        #             "((\w+)(\.\w\w+)"    +   # Server.xx (mandatory)
        #             "|" +                            # servername OR IP
        #             "(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))" + # OR IP (mandatory)  
        #             "(:\d+){0,1}" + # port (mandatory)
        #             "(\/\.*){0,}"    +   # remainder
        #            "$")
        # 
        #=======================================================================
        
        pattern = "^([a-z0-9+.-]+):(?://(?:((?:[a-z0-9-._~!$&'()*+,;=:]|%[0-9A-F]{2})*)@)?((?:[a-z0-9-._~!$&'()*+,;=]|%[0-9A-F]{2})*)(?::(\d*))?(/(?:[a-z0-9-._~!$&'()*+,;=:@/]|%[0-9A-F]{2})*)?|(/?(?:[a-z0-9-._~!$&'()*+,;=:@]|%[0-9A-F]{2})+(?:[a-z0-9-._~!$&'()*+,;=:@/]|%[0-9A-F]{2})*)?)(?:\?((?:[a-z0-9-._~!$&'()*+,;=:/?@]|%[0-9A-F]{2})*))?(?:#((?:[a-z0-9-._~!$&'()*+,;=:/?@]|%[0-9A-F]{2})*))?$"

        pattern = re.compile(pattern, re.IGNORECASE)
     
        if pattern.match(URL): return True
     
        #=======================================================================
        # elif re.match("^\s*(https?://){0,1}localhost\s*[/\.]{0,}$", str(URL), re.IGNORECASE):
        #     return True
        #=======================================================================
        #=======================================================================
        # #These are specific to the urlparse method
        # scheme          = kwargs.pop('scheme', None)
        # allow_fragments = kwargs.pop('allow_fragments', None)
        # 
        # if urlparse(URL, scheme, allow_fragments): return True
        #=======================================================================
        else:
            # If error was passed in as True, then raise error on failure
            if kwargs.pop('error', False):
                err = ''.join(["URL/URI:'", str(URL), "' does not match expected format."])        
                raise NameError(e)
            # Otherwise just return False
            return False
    # Map old for compatibility
    checkURL = checkURI

    def isFileURI(self, value):
        p = "^file://.*$"
        if re.match(p, value): return True
        else: return False
                      
    def checkS3(self, URI):
         # check for white spaces
        p = '\s'
        if re.search(p, URI): return False # check for white spaces
    
        # Check overall structure
        p = ("^(s3://)" +         # s3 header 
             "([^/]*)"  +         # Bucket name
             "((/*\S{1,})*[^/])$" # Everything else, do not end in '/'
             )
        _re = re.compile(p, re.IGNORECASE | re.UNICODE)
        match = _re.match(ORIGINAL_S3PATH)
        if not match: return False
        
        return True
            
    def checkOS(self, os = None):
        """
        checkOS(['os'])
        
        DESCRIPTION
            checkOS returns either the OS platform (if called with no option), 
            or a True/False if the passed option matches the OS type.
            
        OPTIONS
            os = a STRING containing the name of the os to be identified. If the 
                 platform matches the 'os', checkOS will return True, 
                 otherwise it returns False.
                 
                Acceptable 'os' parameters are:
                    windows = T if windows OS
                    win     = T if windows OS
                    win32   = T if windows 32 bit specifically
                    win64   = T if windows 64 bit specifically
                    freebsd = T if FreeBSD specifically
                    gnu     = T if GNU OS specifically
                    linux   = T if linux, or GNU, or FreeBAD
                    unix    = T if Solaris, or riscos, or FreeBSD
                    *nix    = T if linux, or GNU, or FreeBAD, or Solaris, 
                              or riscos, or FreeBSD
                    risc    = T is riscos
                    atheos  = T is atheos
                    solaris = T if solaris, or sunos
        """
        return _checkOS(os)
    
    def isSanitized(self, value, blacklist = None, system = "local"):
        """
        :NAME:
            isSanitized(<string>, blacklist = [<list of strings>])
            
        :DESCRIPTION:
            checkSanitized() will check the passed-in string for potential security 
            risk keywords. If 'blacklist' is not passed, it will use a default
            list of keyword risks (recommended) appropriate to the operating system. 
            Passing in a 'blacklist' requires a deep understanding of the mechanisms 
            of checkSanitized() and of how regex searches are performed, and is 
            not recommended.  
            
            checkSanitized() returns True (no risks, string is sanitized) or 
            False (risks found).
            
            The check is done via a regex 'search' function, meaning any appearance 
            of the keyword in the string will return a 'False' response. This means
            traditional regex expressions can be included, and spaces are critical 
            when creating a blacklist keyword. 
            
            For example, searching for specific words as 'rm' is different than 
            ' rm '. Consider the string 'charactermove' (containing 'rm') which 
            does not contain a risk) versus the string 'rm passwd' 
            (containing 'rm ') which is unquestionably a risk.
            
            Default risk keywords include ';' and other database related concerns 
            such as 'drop ', 'insert ', 'delete '. When using checkSanitized() to 
            check select statements for databases, a blacklist must be passed in
            which overrides all defaults including these. 
            
        :ARGUMENTS:
            <string>:   A string to be checked. If a non-string is passed, it will
                        be converted to a string and checked. 
                        
            blacklist:  A list of strings to be used as keywords against which the 
                        string will be checked. Full regex expressions can be used
                        as individual string keywords within this list. SPACES
                        within keywords ARE NOT IGNORED, meaning 'rm' and 'rm ' will
                        produce different results.   
    
                        Default risk keywords include ';' and other database related 
                        concerns such as 'drop ', 'insert ', 'delete '. When using 
                        checkSanitized() to check select statements for databases, 
                        a blacklist must be passed in which overrides all defaults 
                        including these. 
    
        :RETURNS:
            True or False
            
        :USAGE:
            s = 'my text string'
            if isSanitized(s):
                <continue with code>
            else:
                <raise error message>
        """    
        if   re.search("lin",   str(system)): return _linux_sanitize(value, blacklist)[0]
        elif re.search("darwin",str(system)): return _OSX_sanitize(value, blacklist)[0] # MUST COME BEFORE 'win'
        elif re.search("win",   str(system)): return _windows_sanitize(value, blacklist)[0]
        elif re.search("mac",   str(system)): return _OSX_sanitize(value, blacklist)[0]
        elif re.search("osx",   str(system)): return _OSX_sanitize(value, blacklist)[0]
        else:
            err = ''.join(["checks.checkSanitized: ", "Unable to sanitize for operating system '", str(_os), "'." ]) 
            raise AttributeError(err)
        #=======================================================================
        # _os = self.checkOS()
        # s = str(s)
        # 
        # # Check the always sanitized stuff
        # # If blacklist is NOT NONE, then dont do this
        # if blacklist is None:
        #     """
        #     NOTE: THE POSITIONS OF THE SPACES IS CRITICAL HERE.
        #     Commands are only commands if spaces before and/or after
        #     Think about spaces here
        #     """
        #     # Think about spaces here
        #     _blacklist = [
        #                  ' delete ', # General
        #                  ' drop ' ,# Database
        #                  ' insert ', # Database
        #                 ]
        #     
        #     # Return here. No need to continue if failes. 
        #     if (_checkSanitized(s, _blacklist) is False): return False
        #     
        # # These get run regardless of blacklist = None
        # 
        # if   self.checkOS('linux2')  : return _checkLinuxSanitized(s, blacklist)
        # elif self.checkOS('win')     : return _checkWindowsSanitized(s, blacklist)
        # elif self.checkOS('darwin')  : return _checkOSXSanitized(s, blacklist)
        # else:
        #     err = ''.join([
        #                    "checks.checkSanitized: ", 
        #                    "Unable to sanitize for operating system '", 
        #                    str(_os),
        #                    "'."
        #                    ]) 
        #     raise AttributeError(err)
        #=======================================================================
    checkSanitized = isSane = isSanitized
    
    
    def contents(self, value):
        """"""
        # Try unpickling first
        try:
            return pickle.load( open( value, "rb" ) )
        # Pickle will fail with any number of errors if this is not a pickly file. 
        # So just catch everything, and assume not a valid pickle
        except Exception as e:
            pass # Not a pickle
        # Now try as a regular file
        try: 
            FH = open(value, 'r', 0)
            return FH.read()        
        except IOError as e:
            pass
    #         err = "{C}.{M}: Unable to open file for reading ('{F}'). ".format(C = self.__class__.__name__, M = inspect.stack()[0][3], F = value)
        # Just return string
        return str(value)

    def sanitize(self, value, blacklist = None, system = "local"):
        """
        :NAME:
            sanitize(
                        <string>, 
                        [blacklist = <list_of_regex_strings>, 
                        remove = <regex_string_of_characters>]
            )
        
        :DESCRIPTION:
            sanitize() removes any illegal words and characters from a string.
            
        :PARAMETERS:
            value    : The string to be sanitized. Must be a string. If it's not
                      it will be converted to a string and a string is returned. 
                    
            blacklist: A list of regex expeessinos (as strings) which will be 
                      matched in their entirety against the string, and removed. 
                      The default (for linux) is:
                        [
                           ';*\s*sudo\s', 
                           ';*\s*su\s',
                           ';*\s*bash'
                           ';*\s*rm -{0,1}[RrFf]*',
                           ';*\s*chmod\s*',
                           ';*\s*chown\s*',
                           ';', # ALWAYS PUT ME LAST 
                           ]
                      
            remove   : A regex list of characters which will be stripped from 
                       the final string. This is done AFTER the words are 
                       removed. ALWAYS pass as a string between []. 
                       I.e.
                           [0-9\s]
                        (which removes all spaces and numbers form the string. 
        
        :RETURNS:
            A cleaned string.
        """
        value = str(value)
        if re.search("local", str(system)): 
            system = _checkOS()
        system = str(system.lower())
        
        if   re.search("lin",   str(system)): return _linux_sanitize(value, blacklist)[1]
        elif re.search("darwin",str(system)): return _OSX_sanitize(value, blacklist)[1] # MUST COME BEFORE 'win'
        elif re.search("win",   str(system)): return _windows_sanitize(value, blacklist)[1]
        elif re.search("mac",   str(system)): return _OSX_sanitize(value, blacklist)[1]
        elif re.search("osx",   str(system)): return _OSX_sanitize(value, blacklist)[1]
        else:
            err = ''.join(["checks.checkSanitized: ", "Unable to sanitize for operating system '", str(_os), "'." ]) 
            raise AttributeError(err)

    #===============================================================================
    # def checkTempdir(_dir, create = False):
    #     """
    #     Checks the existence of the temp directory passed in. 
    #     If directory exists, returns the directory name. (No True/False)
    #     If it doesn't exist, create = True attempts to create it. 
    #     Must give FULL DIRECTORY PATH
    #     Raises error on failure (No True/False)
    #     """
    #     err_does_not_exist = ''.join(["Directory:'", str(_dir), "' ", 
    #                                   "does not exist."])
    #     
    #     err_cannot_create = ''.join(["Unable to create ", 
    #                                  "the .temp directory:'", str(_dir),  "'.", 
    #                                  ])
    # 
    #     err_not_full_path = ''.join(["Directory:'", str(_dir), "' ", 
    #                                   "does not appear to be a full path."])
    #     
    #     if _dir is None: 
    #         raise ValueError(err_not_full_path)
    #     else:
    #         _dir = ''.join(c for c in str(_dir) if c not in '     ')
    #     
    #     if _dir.lower() == 'system':
    #         raise NotImplementedError('Use of system temp directory not yet implemented.')
    # 
    #     if ((not _dir.startswith(delim())) or (not _dir.endswith(delim()))):    
    #         raise ValueError(err_not_full_path)
    #         
    #     _dir = check_directory_format(_dir)
    #     
    #     if ntpath.exists(_dir): 
    #         return _dir
    # 
    #     else:
    #         if create:
    #             try:
    #                 os.makedirs(_dir)
    #                 return _dir
    #             except Exception as e:
    #                 raise type(e)(e.message + 
    #                               err_cannot_create + 
    #                               "Please check the path and  permissions. ")                
    #         else:
    #             raise IOError(err_does_not_exist + "create = False.")                
    #===============================================================================
    def isFile(self, path ):
        return _fileExists(path)
    
    def isDir(self, path, *args, **kwargs):
        return _dirExists(path, *args, **kwargs)
    
    def isDirectory(self, path):
        return isDir(path)
    
    def isFolder(self, path):
        return _dirExists(path)
    
    def isDict(self, _dict):
        try:
            _dict.keys()
            return True
        except (AttributeError):
            return False
    checkDict = isDict
                      
    def isList(self, _list):
        try:
            _list.append("DELETEMELISTCHECKVARIABLE")
            _list.pop(len(_list)-1)
        except AttributeError as e:
            return False
        except Exception as e:
            raise
        return True
    checklist = isList
                      
    def isObject(self, obj):
        if (
            ("object" in str(obj).lower()) or
            ("instance" in str(obj).lower())
             ):
            return True
        else:
            return False
    checkObject = isObject
                      
    def isPathFormat(self, path, full = False, relative = False, trailing = False):
        """
        :NAME:
        isPathFormat(path, [full = False, relative = False, trailing = False])
        
        :DESCRIPTION:
        Checks if the format of a string is consistent with the OS's path format. 
        Does not check whether the path exists.
        This implicitly verifies the correct OS is checked for 
        """
#         _delim = self.directory_deliminator()
        path = str(path)
        # Build directory forbidden character list, as a [anyof]
        invalid_chars = ''.join([
                    "[",
                    "\<", # (less than)
                    "\>", # (greater than)
                    "\:", # (colon)
                    '\\\"', # (double quote)
                    "\\\'", # (Single quote)
                    "\|", # (vertical bar or pipe)
                    "\?", # (question mark)
                    "\*", # (asterisk)   
                    "\s", # space chars                
                     ])
    
        # Add the opposite OS directory delimiter
        if "/" in self._delim: invalid_chars = invalid_chars + "\\\\"
        else:             invalid_chars = invalid_chars + "/"
        
        #Finish it off
        invalid_chars = invalid_chars + "]"
        
        # Check for forbidden characters
        if re.search(invalid_chars, path): return False
        # If here, all chars are legal. Just check start and finish
        # If full path is required, start with first
        if (full) and (not path.startswith(self._delim)):
#             print('checks.isPathFormat:FALSE not startswith', _delim #3333 
            return False
        # if relative, must start with dot slash
        if (relative) and (not path.startswith("." + self._delim)):
#             print('checks.isPathFormat:FALSE not  . and ', _delim #3333 
            return False
        # If trailing the a trailing delimiter is required
        if (trailing) and (not path.endswith(self._delim)):
#             print('checks.isPathFormat:FALSE not endswith', _delim #3333 
            return False
        # Otherwise, if here, everything aligns
        return True
        
    #===============================================================================
    #     p = re.compile("^(([a-zA-Z]:\\\)|(\.\\\)|(\.\.\\\)).*$")
    # 
    #     _path = str(_path)
    #     _delim = directory_deliminator()
    #     
    #     if re.search(" ", _path): return False
    #     
    #     if not _path.endswith(_delim): _path = ntpath.dirname(_path) + _delim
    #     
    #     if ( 
    #         ( (_path.startswith('.')) or (_path.startswith(_delim)) ) and 
    #         (_path.endswith(_delim)) 
    #        ):
    #         return True 
    #     else:
    #         return False
    #===============================================================================
    checkPathFormat = isPathFormat

    def isWindowsPath(self, path):
        return _windowsPathFormat(path)
    
    def isLinuxPath(self, path):
        return _linuxPathFormat(path)
    
    def isPathType(self, path):
        if self.isWindowsPath(path): return 'win'
        elif self.isLinuxPath(path): return 'nix'
        else:
            return None 

    def re_match(self, p, s, *args, **kwargs):
        return _re(p, s, 'match', *args, **kwargs)        

    def re_search(self, p, s, *args, **kwargs):
        return _re(p, s, 'search', *args, **kwargs)        

    def CheckYN(self, prompt, fullword = False, bool = False):
        """"""
        def _true():
            if bool: return True
            else:    return "YES"
            
        def _false():
            if bool: return False
            else:    return "NO"

        # Work    
        yn = input(prompt)
        if "yes" in yn.lower(): 
            return _true()

        elif "y" in yn.lower():
            if fullword:
                print("Please type the full word 'yes'")
                return self.CheckYN(prompt, fullyes, bool)
            else:
                return _true()
    
        if "no" in yn.lower(): 
            return _false()

        else:
            if fullword:
                print("Please type the full word 'no'")
                return self.CheckYN(prompt, fullword, bool)
            else:
                return _false()

    def isYes(self, prompt, fullword = False, *args, **kwargs):
        # Override with bool = True
        return self.CheckYN(prompt, fullword = fullword, bool = True)

    def isNo(self, prompt, fullword = False, *args, **kwargs):
        # Override with bool = True
        result = self.CheckYN(prompt, fullword = fullword, bool = True)
        # CheckYN return True for yes and False for no. 
        # reverses true and false, since this "isNo"
        if result is True: return False
        else:              return True 

    def split_path(self, path):
        raise NotImplementedError("checks.split_path is not yet implemented.")
        folders = []
        while 1:
            path, folder = os.path.split(path)
        
            if folder != "":
                folders.append(folder)
            else:
                if path != "":
                    folders.append(path)
        
                break        
    
if __name__ == "__main__":
    o = Checks()
    s ="/etc; hello"
    blacklist = ["/", "etc"]
    print(o.sanitize(s, 
#                      blacklist, 
#                      system
                     ))
#    if o.CheckYN("y/N") == "YES": print("YES")
    #=== Test sanitize =================================================
    # s = "This sudo is rm -rf not an OK string; kill "
    # bool,s = o.sanitize(s)
    # print(bool)
    # print(s)
    # print("===")
    # print(o.isSane(s))
    #===================================================================
          