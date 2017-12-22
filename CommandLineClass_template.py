#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__      = "Mike Rightmire"
__copyright__   = "Universitäts Klinikum Heidelberg, Section of Bioinformatics and Systems Cardiology"
__license__     = "Not licensed for private use."
__version__     = "0.9.0.0"
__maintainer__  = "Mike Rightmire"
__email__       = "Michael.Rightmire@uni-heidelberg.de"
__status__      = "Development"


from argparse       import ArgumentParser
# ConfigHandler disabled until py3 update
# from common.confighandler  import ConfigHandler 
# loghandler disabled until bugfix in Jessie access to self.socket.send(msg)
# from common.loghandler     import log 
from common.checks         import Checks
checks = Checks()
_delim = checks.directory_deliminator()
from common.loghandler import log
from inspect import stack

import abc
import inspect
import ntpath
import os

class SuperClassName(metaclass=abc.ABCMeta):
    def __init__(self, parser = {}, *args, **kwargs):
        self.parser = parser
        self.args   = args
        self.kwargs = kwargs         
        self._set_config(parser, args, kwargs) # NEVER REMOVE
                
    def _arg_parser(self, parser):
        """
        :NAME:
        _arg_parser
        
        :DESCRIPTION:
        Put all the argparse set up lines here, for example...
            parser.add_argument('--switch', '-s', 
                                action ="store", 
                                dest   ="variable_name", type=str, default = '.', 
                                help   ='Starting directory for search.'
                                )
        
        :RETURNS:
            Returns the parser object for later use by argparse
            
        """
        ### ALWAYS SET DEFAULTS IN @property ##################################
        parser.add_argument('--someparam', '-P', action="store", dest="SOMEPARAM", type=str, default = None, 
                            help='Some initial parameters.')
        parser.add_argument('--logfile', '-L', action="store", dest="LOGFILE", type=str, 
                            help='Logfile file name or full path.\nDEFAULT: ./classname.log')
        parser.add_argument('--log-level', '-l', action="store", dest="LOGLEVEL", type=str, 
                            help='Logging level.\nDEFAULT: 10.')
        parser.add_argument('--screendump', '-S', action="store", dest="SCREENDUMP", type=str,  
                            help='For logging only. If "True" all logging info will also be dumped to the terminal.\nDEFAULT: True.')
        parser.add_argument('--create-paths', '-C', action="store", dest="CREATEPATHS", type=str, 
                            help='For logging only. If "True" will create all paths and files (example create a non-existent logfile.\nDEFAULT: True')
        return parser
    
    def _set_config(self, parser, args, kwargs):
        """"""
        # Set class-wide
        self.app_name = self.__class__.__name__
#         self.CONF   = ConfigHandler()# ConfigHandler disabled until py3 update
        self.ARGS   = args
        self.KWARGS = kwargs        
        # Convert parsed args to dict and add to kwargs
        if isinstance(parser, ArgumentParser):
            parser = self._arg_parser(parser)
            parser_kwargs = parser.parse_args()
            kwargs.update(vars(parser_kwargs))

        elif isinstance(parser, dict):
            kwargs.update(parser)
            
        else:
            err = "{C}.{M}: Parameter 'parser' ({P}) must be either an Argparse parser object or a dictionary. ".format(C = self.app_name, M = inspect.stack()[0][3], P = str(parser))
            raise ValueError(err)
        
        # #=== loghandler disabled until bugfix in Jessie access to self.socket.send(msg)
        # # Here we parse out any args and kwargs that are not needed within the self or self.CONF objects
        # # if "flag" in args: self.flag = something
        ### ALWAYS SET DEFAULTS IN @property #################################
        # # Logging
        self.logfile        = kwargs.pop("LOGFILE", ''.join(["./", self.app_name, ".log"]))
        self.log_level      = kwargs.pop("LOGLEVEL", 10)
        self.screendump     = kwargs.pop("SCREENDUMP", True)
        self.create_paths   = kwargs.pop("CREATEPATHS", True)
        #=== loghandler bugfix in Jessie access to self.socket.send(msg)
        # Only use actual filesystem file for log for now
        # Log something
        log.debug("Starting  {C}...".format(C = self.app_name), 
                 app_name     = self.app_name,
                 logfile      = self.logfile, 
                 log_level    = self.log_level, 
                 screendump   = self.screendump, 
                 create_paths = self.create_paths, 
                 )
        # Start params here
        self.someparam      = kwargs.pop("SOMEPARAM", 'MyParam')

            
    @property
    def someparam(self):
        try:
            return self.SOMEPARAM
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @someparam.setter
    def someparam(self, value):
        if value is None: value = "MyParam"
        _value = str(value)
        # Do checks and such here
        if (not _value):
            err = "Attribute '{A} = {V}' does not appear to be valid for reason.".format(A = str(stack()[0][3]), V = _value)
            log.error(err)
            raise ValueError(err)
        else:
            self.SOMEPARAM = _value
    
    @someparam.deleter
    def someparam(self):
        del self.SOMEPARAM

    @property
    def logfile(self):
        try: return self.LOGFILE
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @logfile.setter
    def logfile(self, value):
        if value is None: value = ''.join(["./", self.app_name, ".log"])
        _value  = str(value)
        _dir    = ntpath.dirname(_value)
        _file   = ntpath.basename(_value)
        _basefilename, _ext = os.path.splitext(_file)
        # Do checks and such here
        if (_dir == "") or (_dir.startswith(".")): _dir = os.getcwd() + _delim
        _value = _dir + _file 
        self.LOGFILE = _value
    
    @logfile.deleter
    def logfile(self):
        del self.LOGFILE

    @property
    def log_level(self):
        try: return self.LOGLEVEL
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @log_level.setter
    def log_level(self, value):
        if value is None: value = 10
        try: self.LOGLEVEL = int(value)
        except (ValueError, TypeError):
            _value = str(value).upper()
            if   "CRIT"   in _value: self.LOGLEVEL = 50
            elif "ERR"    in _value: self.LOGLEVEL = 40
            elif "WARN"   in _value: self.LOGLEVEL = 30
            elif "INF"    in _value: self.LOGLEVEL = 20
            elif "D"      in _value: self.LOGLEVEL = 10
            elif "N"      in _value: self.LOGLEVEL = 0
            else:
                err = "Unable to determine log level value from'{V}'".format(str(value))
                raise ValueError(err)
                    
    @log_level.deleter
    def log_level(self):
        del self.LOGLEVEL

    @property
    def screendump(self):
        try: return self.SCREENDUMP
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @screendump.setter
    def screendump(self, value):
        if value is None: value = None
        if value:   self.SCREENDUMP = True
        else:       self.SCREENDUMP = False
                    
    @screendump.deleter
    def screendump(self):
        del self.SCREENDUMP

    @property
    def create_paths(self):
        try: return self.CREATEPATHS
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
            log.error(err)
            raise ValueError(err)
        
    @create_paths.setter
    def create_paths(self, value):
        if value is None: value = True
        if value:   self.CREATEPATHS = True
        else:       self.CREATEPATHS = False
                    
    @create_paths.deleter
    def create_paths(self):
        del self.SCREENDUMP
    
    @abstractmethod
    def main(self):
        """"""
        raise NotImplementedError()
        

class ClassName(SuperClassName):
    def __init__(self, parser = {}, *args, **kwargs):
        super().__init__(parser, args, kwargs)
        self.main()
        
    def main(self):
        pass
    
if __name__ == '__main__':
    parser = ArgumentParser()
    object = ClassName(parser)
