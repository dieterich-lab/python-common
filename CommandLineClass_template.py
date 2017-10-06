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

import inspect

class ClassName(object):
    def __init__(self, parser = {}, *args, **kwargs):
        self._set_config(parser, args, kwargs)
        self.main()
                
    @property
    def start_dir(self):
        try:
            return self.START_DIR
        except (AttributeError, KeyError, ValueError) as e:
            err = "Attribute {A} is not set. ".format(A = str(stack()[0][3]))
#             log.error() # loghandler disabled until bugfix in Jessie access to self.socket.send(msg)
            raise ValueError(err)
        
    @start_dir.setter
    def start_dir(self, value):
        _value = str(value)
        if not os.path.isdir(_value):
            err = "The value passed in for attribute {A} ({V}) does not appear to be an existing directory.".format(A = str(stack()[0][3]), V = _value)
#             log.error(err)# loghandler disabled until bugfix in Jessie access to self.socket.send(msg)
            raise ValueError(err)
        else:
            self.START_DIR = _value
    
    @start_dir.deleter
    def start_dir(self):
        del self.START_DIR

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
        parser.add_argument('--root', '-r', action="store", dest="START_DIR", type=str, default = None, help='Starting directory for search.')
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
        # # Logging
        # self.logfile    = kwargs.pop('log_leveL', 'system') # Default warning
        # self.log_level  = kwargs.pop('log_leveL', 10) # Default warning
        # self.screendump = kwargs.pop('screendump', True) # Default off
        # self.formatter  = kwargs.pop('formatter', '%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        # self.create_paths = kwargs.pop('create_paths', True) # Automatically create missing paths
        #=======================================================================
        # parser stuff
        self.start_dir = kwargs.pop("START_DIR", '.')
        
        # Everything else goes into the conf
        for key, value in kwargs.iteritems():
            self.CONF.set(key, value)
        
        print(self.__dict__)
        
        #=== loghandler disabled until bugfix in Jessie access to self.socket.send(msg)
        # # Log something
        # log.debug("Running {C}.{M}...".format(C = self.app_name, M = inspect.stack()[0][3]), 
        #          app_name     = self.app_name,
        #          logfile      = self.logfile, 
        #          log_level    = self.log_level, 
        #          screendump   = self.screendump, 
        #          create_paths = self.create_paths, 
        #          )
        #=======================================================================
            
    def main(self):
        """"""
        # loghandler disabled until bugfix in Jessie access to self.socket.send(msg)
#         log.debug("Done.")
        pass
        
    
if __name__ == '__main__':
    parser = ArgumentParser()
    object = ClassName(parser)
