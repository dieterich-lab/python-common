#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# Removal of the "__license__" line or content from  "__license__", or removal
# of "__author__" in this or any constituent # component or file constitutes a
# violation of the licensing and copyright agreement.
# from cgi import logfile
# NOTES:

__author__      = "Mike Rightmire"
__copyright__   = "BioCom Software"
__license__     = "PERPETUAL_AND_UNLIMITED_LICENSING_TO_THE_CLIENT"
__version__     = "0.9.0.0"
__maintainer__  = "Mike Rightmire"
__email__       = "Mike.Rightmire@BiocomSoftware.com"
__status__      = "Development"
##############################################################################
"""
Inception  - 2018-03-05 : Martin Reifferscheid
2018-03-05 -            : Mike Rightmire
"""

from common.checks import Checks
checks = Checks()
_delim = checks.directory_delimiter()
from paramiko import sftp

from common.loghandler import log
from inspect import stack
from stat import S_ISDIR

import abc
import ntpath
import os
import paramiko
import re

#=== GLOBAL PROTECTED DIRECTORIES =====================================
protected_paths = [_delim, # Root dir 
                  "etc", "var", "lib", "home", "usr/local",  
                  "bin",   "dev",  "initrd", "installimage", 
                  "lib32", "libx32", "media", "opt", "proc", 
                  "run", "srv", "tmp", "vmlinuz", "boot", 
                  "installimage", "lib64", "mnt", "root",  
                  "sbin", "sys", "vmlinuz" ]
#======================================================================
        
class SSHsuper(metaclass=abc.ABCMeta): # Change from the template name
    """
    USe this for all properties and hidden methods
    """
    def __init__(self, 
                key = None, 
                known_hosts = None, 
                user = None, 
                password = None, 
                server = None, 
                port = None, 
                *args, **kwargs):
        
        self.user       = user 
        self.password   = password
        self.server     = server
        self.port       = port
        
    @property
    def ssh(self):
        try: return self.SSH
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @ssh.setter
    def ssh(self, value):
        if isinstance(value, paramiko.SSHClient): self.SSH = value
        else:
            err = "Parameter does not appear to be a vailid paramike ssh client object. Value = '{}'".format(str(value))
            log.error(err)
            raise ValueError(err)
    
    @ssh.deleter
    def ssh(self):
        del self.SSH
    
    @property
    def key(self):
        try: return self.KEY
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @key.setter
    def key(self, value):
        self.KEY = value
        #=== Add checks later #333 =====================================
        # if os.path.isfile(value): self.KEYPATH = value
        # else:
        #     err = "Value for 'keypath' ('{V}')does not appear valid or is unreadable.".format(V = str(value))
        #     raise ValueError(err)
        #===============================================================
    
    @key.deleter
    def key(self):
        del self.KEY

    @property
    def keypath(self):
        try: return self.KEYPATH
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @keypath.setter
    def keypath(self, value):
        if os.path.isfile(value): self.KEYPATH = value
        else:
            err = "Value for 'keypath' ('{V}')does not appear valid or is unreadable.".format(V = str(value))
            log.error(err)
            raise ValueError(err)
    
    @keypath.deleter
    def keypath(self):
        del self.KEYPATH
     
    @property
    def server(self):
        try: return self.SERVER
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
    
    @server.setter
    def server(self, value):
        _value = str(value)
        ### Checks later #333
        self.SERVER = _value
        
    @server.deleter
    def server(self):
        del self.SERVER
            
    @property
    def user(self):
        try: return self.USER
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @user.setter
    def user(self, value):
        _value = str(value)
        ### Checks ater #333
        self.USER = _value
        
    @user.deleter
    def user(self):
        del self.USER
            
    @property
    def password(self):
        try: return self.PASSWORD
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @password.setter
    def password(self, value):
        _value = str(value)
        ### Checks ater #333
        self.PASSWORD = _value
        
    @password.deleter
    def password(self):
        del self.PASSWORD

    @property
    def sftp(self):
        try:
            return self.SFTP
        except (AttributeError, KeyError, ValueError) as e:
            self.SFTP = self.ssh.open_sftp()
            return self.SFTP
        
    @sftp.setter
    def sftp(self, value):
        err = "sshhandler.sftp cannot be set manually. "
        log.error(err)
        raise ValueError(err)
    
    @sftp.deleter
    def sftp(self):
        del self.SFTP

    @property
    def port(self):
        try: return self.PORT
        except (AttributeError, KeyError, ValueError) as e:
            err = "Setting parameter 'port' to default of '22'."
            log.warning(err)
            self.PORT = 22
            return self.PORT

    @port.setter
    def port(self,value):
        try: 
            _value = int(value)
            self.PORT = _value
            
        except ValueError as e:
            err = "The parameter for 'port' ('{V}') must be an integer. (ERROR:{E})".format(V = str(value), E = str(e))
            log.error(err)
            raise ValueError(err)
        
    @port.deleter
    def port(self):
        del self.PORT

# === PRIVATE METHODS ==========================================

    def _chown(self, path, uid, gid):
        try: self.sftp.chown(path, uid = uid, gid = gid)
        except Exception as e:
            err = "Unable to change path's ownership to '{U}:{G}' (ERROR: {E})".format(U = str(uid), G = str(gid), E = str(e))
            log.error(err)
    
    def _is_protected_path(self, src):        
        # Error out if src = these directores, 
        # but not subdirectories of these directories
        for dir in protected_paths:
            # spaces + any num / + dir + any num / + spaces + NOT MATCH anything else after these spaces then end
            # The "^" (START) and "$" (END) is added later  
            p = ''.join(["\s*", "[", _delim, "]*", dir, "[", _delim, "]*\s*"])
            # Check for matches an error
            err = "sshhandler._deletedir({S}): appears to have a protected directory in the path. HALTED!".format(S = src)
            # First check without quotes
            pattern = "^" + p + "$" # Start(^) and end ($)
            if re.match(pattern, src): return True # protected dir  
            # Then match inside quotes
            pattern = ".*'" + p + ".*'.*"     # If starts with anything + ' + the pattern + ' + anything
            if re.match(pattern, src):  return True # protected dir
            pattern = '.*"' + p + '.*".*' # If starts with anything + " + the pattern + " + anything
            if re.match(pattern, src):  return True # protected dir
            
        return False # Its OK            
        
    def _deletedir(self, src, euid = None, egid = None):
        """
        """
        # Paramiko doesn't yet delete filled directories...so we need to 
        # use an exec. As such, we sanitze it carefully 
        # first sanitize using checks. This removes anything after a ';'
        src = checks.sanitize(src)
        # Next we disallow ay protected directories
        # Currently linux only
        if self._is_protected_path(src):
            err = "sshhandler._deletedir({S}): appears to have a protected directory in the path. HALTED!".format(S = src)
            raise RuntimeError(err)
        try:
            msg = "Deleting directory '{S}' ...".format(S = src)
            command = ''.join(["rm -rf ", src])
            # Use the main paramiko ssh connection 
            (stdin, stdout, stderr) = self.ssh.exec_command(command)
            #self.sftp.rmdir(src) # This later if they get it fixed
            log.debug(msg + "OK")
        except Exception as e:
            err = msg + "FAILED! (ERROR: {E})".format(E = str(e))
            log.error(err)
            raise type(e)(err)

    def _deletefile(self, src, *args, **kwargs):
        src = self._clean_semi_colon(src)
        src = checks.sanitze(src)

        if _is_protected_path(src):
            err = "sshhandler._deletedir({S}): appears to have a protected directory in the path. HALTED!".format(S = src)
            raise RuntimeError(err)

        msg = ("ssh.deleting: '{S}...".format(S = str(src)))
        try:
           self.sftp.remove(src)
           log.warning(msg + "OK")
        
        except Exception as e:
           msg += "FAILED! (ERROR: {E})".format(E = str(e))
           log.error(msg)

    def _getdir(self, src, dst, skip_on_exist = False, skip = [], euid = None, egid = None):
        """
        _getdir(src, dst, skip_on_exist = False, skip = [], euid = None, egid = None)        
        src must be a directory path. 
        dst must be a directory path. 
        """
        for path,folders,files in self.sftp_walk(src):
            for file in files:
                # You must lstrip any leading delimiter from _subpath
                # Otherwise os.join makes it the leading dir!!! 
                _subpath = path.replace(src, "").lstrip(_delim)
                _dst = os.path.join(dst, _subpath, file)
                _src = os.path.join(path, file)
#                 log.debug("SSHsuper._getdir: Calling '_getfile' with  src = '{}', dst = '{}',  skip_on_exist = '{}',  skip = '{}'".format(_src, _dst, skip_on_exist, skip))
                self._getfile(src = _src, 
                              dst = _dst, 
                              skip_on_exist = skip_on_exist, 
                              skip = skip)

    def _getfile(self, src, dst, skip_on_exist = False, skip = []):
#             try:
                msg = ("ssh.get'ing: '{S}' to '{D}'...".format(S = str(src), D = str(dst)))
                if skip_on_exist:
                    if os.path.exists(dst):
                        # Re-enable for troubleshooting
                        # log.warning(msg + "SKIPPING! (File already exits)")
                        return
                
#                 filename = ntpath.basename(src)
                for item in skip:
                    # Pattern is to find JUST the whole item name in a 
                    # path. I.e. item = ".git" must match "/.git/"
                    # No partial matches like ".gitignore"
                    p = ''.join([_delim, item, _delim]) 
                    if re.search(p, src):
                        # Re-enable for troubleshooting
                        # log.debug("The item '{I}' is from Path '{S}' is in skip list. SKIPPING!".format(I = item, S = src)) 
                        return
                
                # Check for dst dir and create is needed
                _dstdir = ntpath.dirname(dst)
                if not os.path.isdir(_dstdir):
                    log.debug("Creating destination directory: '{}'".format(_dstdir)) 
                    try:
                        os.makedirs(_dstdir, exist_ok=True)
                        log.debug("os.stat({D}) = {R}".format(D = _dstdir, R=str(os.stat(_dstdir)))) #333
                        if not os.path.isdir(_dstdir):
                            err = "Something went wrong creating the directory. 'os.path.isdir({D})' reported 'False'.".format(D = _dstdir)
                            raise Exception(e)
                    except Exception as e:
                        err = "Unable to create directory '{D}' (ERROR:{E}".format(D = _dstdir, E = str(e))
                self.sftp.get(src, dst)
                log.debug(msg + "OK")

#===============================================================================
#             except Exception as e:
#                 msg += "FAILED! (ERROR: {E})".format(E = str(e))
#                 log.error(msg)
# #                 raise RuntimeError(err)
#===============================================================================

    def _make_all_remote_dirs(self, dirpath):
        """
        This rolls through the directory path, and makes any remote 
        directories and subdirectories that do not already exist.
        
        'dirpath' must be the DIRECTORY PATH ONLY (Do NOT include the 
        filename) or you will get weird results.   
        """
        _dirlist = self._split_dir_path(dirpath)

        _remotedir = ""
        for _dir in _dirlist:
            _remotedir = os.path.join(_remotedir,_dir) # Add it to the continuing chain
            # Try will error if dir does not exist on remote end
            test = self.stat_remote_path(_remotedir)
            if test is None:
#             if self.stat_remote_path(_dir) is None:
                log.debug("Making  remote dir '{}'".format(_remotedir))
                self._mkdir(_remotedir)
                #===============================================================
                # try: self.sftp.mkdir(_remotedir) # Make the dir at this level
                # except Exception as e:
                #     err = "sshhandler._make_all_remote_dirs: Failed to make remote directory of '{D}'!. (ERROR: {E})".format(D = _remotedir, E = str(e))
                #     raise type(e)(err)
                #===============================================================
                    
    def _mkdir(self, path):
        msg = ("Creating destination dir: '{D}'".format(D = path))
        try: 
            self.sftp.mkdir(path)
            # if euid: self._chown(_dstroot, euid, egid)
            # if egid: self._change_group(_dstroot, euid, egid)
            log.debug(msg + "OK")
        except Exception as e:
            msg += "FAILED! (ERROR: {E})".format(E = str(e))
            raise type(e)(msg)
        
    def _putdir(self, src, dst, skip_on_exist = False, euid = None, egid = None):
        for root, dirs, files in os.walk(src):
            # Set destination path
            _dstroot = os.path.join(dst,root.replace(src,""))
            # First change to dest dir. Make if does not exist
            try: 
                self.sftp.chdir(_dstroot)
            except Exception as e:
                try: 
                    self.sftp.mkdir(_dstroot)
                    self.sftp.chdir(_dstroot)
                except Exception as e:
                    err = "Unable to make remote directory '{D}' (ERROR: {E})".format(D = _dstroot, E = str(e))
                    raise type(e)(err)
            # Now copy all files in this dir
            for file in files:
                _dstfile = os.path.join(_dstroot, file)
                _srcfile = os.path.join(root, file)
                self._putfile(_srcfile, _dstfile, skip_on_exist)

    def _putfile(self, src, dst, skip_on_exist = False):
        self.sftp.chdir("/")
        _dstpath = ntpath.dirname(dst)
        _dstname = ntpath.basename(dst)
        msg = "Copying local file '{F}' to remote server ...".format(F = str(src))
        try: 
            if skip_on_exist:
                if _dstname in self.sftp.listdir(_dstpath):
                    log.warning(msg + "SKIPPING! (File already exits)")
                    return
        except: pass
        # Roll through the directory path and 
        # make all subdirs at once.
        self._make_all_remote_dirs(_dstpath) 

        try:
            self.sftp.put(src, dst)
            log.debug(msg + "OK")
        except Exception as e:
            err = msg + "FAILED! during copy of local file '{F}' to remote server (ERROR: {E})".format(E = str(e))
            log.error(err)
            raise type(e)(err)
    
    def _split_dir_path(self, path):
        folders = []
        while True:
            path, folder = os.path.split(path)
            if folder == "":
                break 
            else:
                folders = [folder] + folders# Put it at the front
        return folders    
                    
    def sftp_walk(self,remotepath):
        """
        :NAME:
            sftp_walk(remotepath)
            
        :DESCRIPTION:
            sftp_walk is based on os.walk It walks remotepath and yields
            the same data as os.walk, except on the remote system
            
            (Uses ssh)
             
        :PARAMETERS:
            remotepath = The full path of the remote directory.
                         DO NOT include the user or server information 
                         here. That is set at class instantiation. 
        :YIELDS:
            (path,folders,files) on the remote directory (Identical to 
            os.walk)
        """
        # Kindof a stripped down  version of os.walk, implemented for 
        # sftp.  Tried running it flat without the yields, but it really
        # chokes on big directories.
        path=remotepath
        files=[]
        folders=[]
        for f in self.sftp.listdir_attr(remotepath):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        
        yield path,folders,files
        
        for folder in folders:
            new_path=os.path.join(remotepath,folder)
            for x in self.sftp_walk(new_path):
                yield x
                                    
    def stat_remote_path(self, path):
        try:  return str(self.sftp.lstat(path))
        except FileNotFoundError as e: return None 
        except PermissionError as e  : return "exists" # Cant read it but it's there

    def remote_is_file(self, path):
        _stat = stat_remote_path(path)
        if _stat.startswith("-"):
            return True
        
    def remote_is_dir(self, path):
        _stat = stat_remote_path(path)
        if _stat.startswith("d"):
            return True
        
    
    def remote_path_is(self, path):
        if   self.remote_is_dir: return "directory"
        elif self.remote_is_file: return "file"
        else: 
            err = "sshhandler.remote_is: Unable to determine remote file type of '{P}'".format(P = str(path))
        
class SSH(SSHsuper):
    """
    :NAME:
        SSH(key, known_hosts , user, password, server, port) 
        
    :DESCRIPTION:
        A Paramiko based ssh management class, for handling the drudgery
        of ssh transfers. 
        
        SSH IS A SINGLETON CLASS!! This means you onle need to set the 
        configuration parameters ONCE per master script. All subsequent 
        objects instantiated by the master script will inherit the 
        settings. 
        
        THE SSH OBJECT DOES NEED TO BE INSTANTIATED BY EACH SUB-OBJECT
        TO THE MASTER, HOWEVER.
         
    :ATTRIBUTES:
        
        server: The IP or FQDN of the remote server with which to SSH.
        
        port: An integer for the ssh port number. 
        
        key: The FULL PATH of the key FILE (not the key itself).
        
        known_hosts: If a different known_hosts file, other than the 
                     system default, is to be used - pass the FULL PATH 
                     here.
        
        user: The username of the user to ssh. 
              
        password: If a text password is to be used, instead of a key 
                  file, assign it here.
        
    :METHODS:
        get(src, dst, skip_on_exist)
            Use ssh to copy the source (remote system) to the 
            destination (local system). Can be used
            for individual files as well as directories.

        put(src, dst, skip_on_exist)            
            Use ssh to copy the source (localsystem) to the 
            destination (remote system). Can be used
            for individual files as well as directories.

    :RETURNS:
        an SSH object. 
        
    :USAGE:
        from common.sshhandler import SSH
        ssh = SSH(
                  server = "123.1.2.123", 
                  port = "12322,
                  key = "/home/my/private/key", 
                  known_hosts = None, 
                  user = "MyUserName", 
                  password = "NotUsingAkey"
                  )
        ssh.put("/my/local/files/", "/my/remote/files/")
        ssh.get("/my/remote/files/", "/my/other/dir/")           
        
    """
    __exists = False

    def __new__(cls,
                key = None, 
                known_hosts = None, 
                user = None, 
                password = None, 
                server = None, 
                port = None, 
                *args, **kwargs
                ):
        """
        This is a singleton class.

        The __new__ method is called prior to instantiation with __init__.
        If there's already an instance of the class, the existing object is
        returned. If it doesn't exist, a new object is instantiated with
        the __init__.
        """

        # __init__ is called no matter what, so...
        # If there is NOT an instance, just create an instance
        # This WILL run __init__
        # Do NOT set self.__exists here, since if _-exists == True, __init__ is
        # cancelled (it must still run at the first instantiation)
        if not hasattr(cls, 'instance'):
            # Create an instance
            cls.instance = super(SSH, cls).__new__( cls#,                 
#                                                     key = None, 
#                                                     known_hosts = None, 
#                                                     user = None, 
#                                                     password = None, 
#                                                     server = None, 
#                                                     port = None, 
#                                                     *args, **kwargs
                                                     )
            return cls.instance
        # Else if an instance does exist, set a flag since
        # __init__is called, but flag halts completion (just returns)
        else:
            cls.instance.__exists = True
            return cls.instance

    def __init__(self, 
                key = None, 
                known_hosts = None, 
                user = None, 
                password = None, 
                server = None, 
                port = None, 
                 *args, **kwargs
                 ):
        
        # __init__ always runs, regardless of the results of __new__
        # so, If an instance already exists, return (don't run the __init__)
        if self.__exists: return
        
        super().__init__(key, 
                            known_hosts, 
                            user, 
                            password, 
                            server, 
                            port, 
                            *args, **kwargs)
        
        self.ssh        = paramiko.SSHClient()
        
        if key:
            try:  self.keypath = key 
            except Exception as e:
                err = "Private Key ('{K}') raised an error ('{E}'). ".format(K = str(key), E = str(e))
                log.error(err)
                raise ValueError(err)

            try:
                self.key = paramiko.RSAKey.from_private_key_file(self.keypath)
            except Exception as e:
                err = "Private Key ('{K}') raised an error ('{E}'). ".format(K = checks.obfuscate_key(str(self.key)), E = str(e))
                log.error(err)
                raise ValueError(err)
            
        if known_hosts is None:
            # This loads the default in a non-permanent way (cannot be saved)
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#             self.ssh.load_system_host_keys(filename=None)
        else:
            try:
                # This load from a file
                ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
            except Exception as e:
                err = "sshhandler.__init__: Was unable to discern how to handle parameter 'known_hosts' = '{K}'. ({E})".format(K = str(known_hosts), E = str(e))
                log.error(err)
                raise RuntimeError(err)
        
        if key:
            self.ssh.connect(self.server, username=self.user, port = self.port, pkey = self.key)
        else:
            self.ssh.connect(self.server, username=self.user, port = self.port, password = self.password)
            
        log.debug("ssh.connect: '{}'".format(str(self.ssh.connect)))

    def delete(self, src, *args, **kwargs):
        """
        :NAME:
            get(src, dst, skip_on_exist)
            
        :DESCRIPTION:
            Use ssh to copy the source to the destination. Can be used
            for individual files as well as directories.
             
        :PARAMETERS:
            src: The source file or directory (remote system). 

            dst: The destination file or directory (local filesystem).
            
            skip_on_exist: If the destination FILE already exists, don't 
                           copy the file. 
                           DEFAULT: False
                           WARNING: The method does NOT do a checksum, 
                                    It only checks for existence. If the
                                    source file has changed, but has the 
                                    same name, the file will still be 
                                    skipped. USE WITH CAUTION.  
            
        """
        _stat = str(self.sftp.lstat(src))
        if _stat.startswith("d"):
            self._deletedir(src = src)
                        
        elif _stat.startswith("-"):
            filename = ntpath.basename(src)
            self._deletefile(src = src)

        else: 
            err = "Unable to determine if 'src' ({S}) is a file or directory. self.sftp.lstat returned with '{T}'".format(S = str(src), T = _stat)
            log.error(err)
            raise RuntimeError(err)
        
    def put(self, src, dst, skip_on_exist = False):
        """
        :NAME:
            put(src, dst, skip_on_exist)
            
        :DESCRIPTION:
            Use ssh to copy the source to the destination. Can be used
            for individual files as well as directories.
             
        :PARAMETERS:
            src: The source file or directory (local filesystem). 

            dst: The destination file or directory (remote system).
            
            skip_on_exist: If the destination FILE already exists, don't 
                           copy the file. 
                           DEFAULT: False
                           WARNING: The method does NOT do a checksum, 
                                    It only checks for existence. If the
                                    source file has changed, but has the 
                                    same name, the file will still be 
                                    skipped. USE WITH CAUTION.  
            
        """
        if os.path.isfile(src):
            self._putfile(src, dst, skip_on_exist)
                        
        elif os.path.isdir(src):
            self._putdir(src, dst, skip_on_exist)
        
        else: 
            err = "Unable to determine if 'src' ({}) is a file or directory. This can sometimes happen with klugy weird filenames. ".format(str(src))
            log.error(err)
            raise RuntimeError(err)
        
    def get(self, src, dst, skip_on_exist = False, skip = []):
        """
        :NAME:
            get(src, dst, skip_on_exist)
            
        :DESCRIPTION:
            Use ssh to copy the source to the destination. Can be used
            for individual files as well as directories.
             
        :PARAMETERS:
            src: The source file or directory (remote system). 

            dst: The destination file or directory (local filesystem).
            
            skip_on_exist: If the destination FILE already exists, don't 
                           copy the file. 
                           DEFAULT: False
                           WARNING: The method does NOT do a checksum, 
                                    It only checks for existence. If the
                                    source file has changed, but has the 
                                    same name, the file will still be 
                                    skipped. USE WITH CAUTION.  
            
        """
        try: 
            if "dir" in self.remote_path_is(src):
                self._getdir(src = src, 
                              dst = dst, 
                              skip_on_exist = skip_on_exist, 
                              skip = skip)

                        
            elif "file" in self.remote_path_is(src):
                filename = ntpath.basename(src)
                self._getfile(src = src, 
                              dst = dst, 
                              skip_on_exist = skip_on_exist, 
                              skip = skip)

        except Exception as e:
            raise
        
if __name__ == '__main__':
    log.debug(
              'sshhandler', 
              app_name = "sshhandler", 
              log_level = 10, 
              screendump = True,
              logfile = "./sshhandler.log"
              )

    o = SSH(
            key = "/Users/mikes/Documents/Work/Heidelberg/it/mrightmire", 
            #                 known_hosts = , 
            user = "metadata", 
            # password = None, 
            server = "dieterichlab.org", 
#             server = "129.206.148.127", 
            port = 22
             )
#     o.put("/Users/mikes/Documents/tmp/", "/home/mrightmire/tmp/")
    o.get(src = "/home/metadata/metadata/", dst="/Users/mikes/Documents/tmp/sshhandlertest/", skip_on_exist = True, skip = [".git"])
      
        
        
            
