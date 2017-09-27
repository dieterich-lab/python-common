#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================
# USE PYTHON 3 SYNTAX WHERE POSSIBLE
from __future__ import print_function
# ==================================

__author__      = "Mike Rightmire"
__copyright__   = "Universitäts Klinikum Heidelberg, Section of Bioinformatics and Systems Cardiology"
__license__     = "Not licensed for private use."
__version__     = "0.9.0.0"
__maintainer__  = "Mike Rightmire"
__email__       = "Michael.Rightmire@uni-heidelberg.de"
__status__      = "Development"


from argparse       import ArgumentParser
from confighandler  import ConfigHandler
from loghandler     import log 
from checks         import Checks
checks = Checks()

import inspect

class ClassName(object):
    def __init__(self, parser = {}, *args, **kwargs):
        self._set_config(parser, args, kwargs)
        self.main()
                
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
        parser.add_argument('--root', '-r', action="store", dest="start_dir", type=str, default = '.', help='Starting directory for search.')
        return parser
    
    def _set_config(self, parser, args, kwargs):
        """"""
        # Set class-wide
        self.app_name = self.__class__.__name__
        self.CONF   = ConfigHandler()
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
        
        # Here we parse out any args and kwargs that are not needed within the self or self.CONF objects
        # if "flag" in args: self.flag = something
        # Logging
        self.logfile    = kwargs.pop('log_leveL', 'system') # Default warning
        self.log_level  = kwargs.pop('log_leveL', 10) # Default warning
        self.screendump = kwargs.pop('screendump', True) # Default off
        self.formatter  = kwargs.pop('formatter', '%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        self.create_paths = kwargs.pop('create_paths', True) # Automatically create missing paths
        # parser stuff
        self.start_dir = kwargs.pop("start_dir", '.')
        
        # Everything else goes into the conf
        for key, value in kwargs.iteritems():
            self.CONF.set(key, value)
        
        print(self.__dict__)
        
        # Log something
        log.debug("Running {C}.{M}...".format(C = self.app_name, M = inspect.stack()[0][3]), 
                 app_name     = self.app_name,
                 logfile      = self.logfile, 
                 log_level    = self.log_level, 
                 screendump   = self.screendump, 
                 create_paths = self.create_paths, 
                 )
            
    def main(self):
        """"""
        log.debug("Done.")
        
    
if __name__ == '__main__':
    parser = ArgumentParser()
    object = ClassName(parser)
