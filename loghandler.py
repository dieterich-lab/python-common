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
__version__     = "0.9.9.0"
__maintainer__  = "Mike Rightmire"
__email__       = "Mike.Rightmire@BiocomSoftware.com"
__status__      = "Development"
##############################################################################

"""
LogHandler IS USED BY BOTH ConfigHandler and ErrorHandler.
AS SUCH, NEITHER CAN BE IMPLEMENTED IN THESE CLASSES WITHOUT WREAKING HAVOC
"""
# from inspect import stack

from common.checks import Checks

import datetime
import time
import traceback
# import inspect
import logging
import logging.handlers
import os
import re
import sys

class log(object):
    """
    :NAME:
    loghanlder.log('message', [KW-params])

    :DESCRIPTION:
    'log' is an interface and controller for the Python module 'logging'. It
    functions using the same basic interface as the 'logging', but handles the
    instantiation and management blindly in the backend.

    from loghandler import log

    log.info( "I automatically instantiate the logging object.",
              app_name   = "MyApplication",
              logfile    = "./MyApplication.log",
              log_level  = 10,
              screendump = True,
              formatter  = '%(asctime)s-%(name)s-%(levelname)s-%(message)s',
              create_paths = True
             )

    log.critical('message')
    log.error('message')
    log.warning('message')
    log.info('message')
    log.debug('message')

    log.debug("I alter the existing logging object's parameters.",
              app_name   = "MyApp",
              logfile    = "./DiffLogName.log",
             )


    :ARGUMENTS:
    app_name:     The friendly name of the application actually instantiating a log
                  object. This is the name used to create a python "logging.logger"
                  instance, and the name that will appear next to the data in
                  the log file to identify what application generated the log
                  information.

                  MANDATORY: No default at this time, however does not need to
                          be set if the setLogger object exists and is called by
                          a child script or process.


                  DEFAULTS TO: loghandler

    screendump:   If True, all lines dumped to the logfile will also
                  appear on the screen (stderr).

                  DEFAULTS TO: False

    formatter:    A string which is passed TO the Python logging
                  formatter object.

                  DEFAULTS TO:
                  '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    create_paths: If True, an attempt to change the logfile to a
                  directory/fle path that does not exist will cause
                  the loghandler object to silently create the path and
                  filename.

                  DEFAULTS TO: True

    logfile:      The FUL PATH (fully qualified path and fielname) where
                  log data will be written to disk. If a file name only
                  is given, the existing path of the calling applicaiton
                  is used AFTER being converted to the fully qualified
                  path.

                  DEFAULTS TO: ./loghandler.log

    log_level: The logging object's "log level" as defined by the Python
               "logging" module. This sets the level of message that is actually
               passed to the logger to be included in the logfile.

               Can be passed as a number between 0 and 50.

               Can be passed as one of the following strings:
                 critical
                 error
                 warning
                 info
                 debug

               DEFAULTS TO: 40 (ERROR)

    :METHODS:
    None.

    :RETURNS:
    Nothing. 'log' is never instantiated as an object, and will error if the
    attempt is made.

    :USAGE:
    'log' is imported and used directly via @classmethods.

    Anytime parameters are passed in addition to the message to be logged,
    these parameters are used to instantiate or change the object behind
    the scenes.

    from loghandler import log

    var = 1

    log.info( "I instantiate the logging object",
              app_name   = "MyApplication",
              logfile    = "./MyApplication.log",
              log_level  = 10,
              screendump = True,
             )

    log.info("var was set to " + str(var))

    log.info( "I change the app name.",
              app_name   = "MyApp",
             )

    (MyApp.log)
    2014-12-23 15:35:42,510 - MyApplication - INFO - I instantiate the logging object
    2014-12-23 15:35:42,511 - MyApplication - INFO - var was set to 1
    2014-12-23 15:35:43,000 - MyApp - INFO - I change the app name.

    """
    @classmethod    
    def _message(self, value):
        try:value = value.encode().decode()
        except AttributeError: value = str(value)
        while len(value) > 1024: # limit for some logfiles
            value = value[:len(value) - 1]
        return value
        
    
    """ CLASSMETHODS ======================================================="""
    @classmethod
    def _setLogger(self, *args, **kwargs):
        """
        This determines if a logging singleton has been created, if not it
        creates one...and then returns the (possibly modified) kwargs
        for use by the Python logger call.
        """            
        # Always check for useLogger first. It determines the remaining parameters
        useLogger    = kwargs.pop('useLogger',        '')
        try:
            # Get the existing logger object. Will error if does not exist
            # DO NOT use getLogger!! It would create a new object
            _logger = logging.Logger.manager.loggerDict[useLogger]
            # Continue if logger found
            # Set logfile
            logfile = 'UNCHANGED' # Default if filehandler not found
            for handler in _logger.__dict__['handlers']:
                if isinstance(handler, logging.FileHandler):
                    logfile = str(handler.__dict__['stream']).split()[2]
                    logfile = ''.join(c for c in logfile if c not in "\"\'\,")
            
            log_level = sys.maxsize
            for handler in _logger.__dict__['handlers']:
                log_level = handler.__dict__['level'] if handler.__dict__['level'] < log_level else log_level
            if log_level == sys.maxsize: log_level = 'UNCHANGED'
            
            screendump = 'UNCHANGED'    
            for handler in _logger.__dict__['handlers']:
                if isinstance(handler, logging.StreamHandler): screendump = True
        # No logger by name of useLogger
        except KeyError as e: 
            _logger     = False
            logfile     = 'UNCHANGED'
            log_level   = 'UNCHANGED'
            screendump  = 'UNCHANGED'
        # Ups something else fubar'ed
        except Exception as e: 
            raise type(e)(e.message)
        # REGARDLESS, ALWAYS TURN OFF useLogger VARIABLE FROM REUSE ##########
        del useLogger
        #####################################################################
        # Regardless of instance status, kwargs still needs to be stripped of
        # the loghandler keywords.
        app_name     = kwargs.pop('app_name',       'UNCHANGED') # Not standard logger value
        # Special vars ###############################
        logfile     = kwargs.pop('logfile',          logfile)
        log_level   = kwargs.pop('log_level',        log_level)
        screendump  = kwargs.pop('screendump',       screendump)
        ###############################################
        format       = kwargs.pop('format',         'UNCHANGED') # Not standard logger value
        create_paths = kwargs.pop('create_paths',   'UNCHANGED') # Not standard logger value
        migrate      = kwargs.pop('migrate',        'UNCHANGED') # Not standard logger value
        # Be sure instantiate is sent as True
        logger = SetLogger(
                            app_name     = app_name,
                            logfile      = logfile,
                            log_level    = log_level,
                            screendump   = screendump,
                            format       = format,
                            create_paths = create_paths,
                            migrate      = migrate, 
                            instantiate  = True # MUST BE TRUE
                            )

        return logger, kwargs

    # LOGGING OVERRIDES========================================================

    @classmethod
    def critical(self, message, *args, **kwargs):
        """"""
        message = log._message(message)
        logger, kwargs = log._setLogger(*args, **kwargs)
        return logger.critical(message, *args, **kwargs)

    @classmethod
    def error(self, message, *args, **kwargs):
        """"""
        message = log._message(message)
        logger, kwargs = log._setLogger(*args, **kwargs)
        return logger.error(message, *args, **kwargs)

    @classmethod
    def warning(self, message, *args, **kwargs):
        """"""
        message = log._message(message)
        logger, kwargs = log._setLogger(*args, **kwargs)
        return logger.warning(message, *args, **kwargs)

    @classmethod
    def info(self, message, *args, **kwargs):
        """"""
        message = log._message(message)
        logger, kwargs = log._setLogger(*args, **kwargs)
        return logger.info(message, *args, **kwargs)

    @classmethod
    def debug(self, message, *args, **kwargs):
        """"""
        #####
        # Use these later to improve formatting
        # Allowing different caller files to be listd in the log line
#         curframe = inspect.currentframe()
#         calframe = inspect.getouterframes(curframe, 2)
#         print 'caller name:', calframe[1][1]
        message = log._message(message)
        logger, kwargs = log._setLogger(*args, **kwargs)
        return logger.debug(message, *args, **kwargs)


class SetLogger(object):
    """
    :NAME:
    SetLogger( app_name,
               [logfile,
                log_level,
                screendump,
                create_paths])

    :DESCRIPTION:
    setLogger is a log object manager intended to handle the details of
    creating and altering a logger.

    The setLogger class is a singleton, meaning once an object is created by a
    calling script, all CHILD SCRIPTS attempting to instantiate a setLogger
    object will - in actuality - receive the existing object.

    The advantage of this is that each object, function or
    child process of the original script can simply call setLogger once and
    in-the-blind to continue logging appropriately.

    SetLogger IS ONLY INTENDED TO BE CALLED BY THE ABOVE 'log' class.

    :ARGUMENTS:
    app_name:     The friendly name of the application actually instantiating a log
                  object. This is the name used to create a python "logging.logger"
                  instance, and the name that will appear next to the data in
                  the log file to identify what application generated the log
                  information.

                  MANDATORY: No default at this time, however does not need to
                          be set if the setLogger object exists and is called by
                          a child script or process.


                  DEFAULTS TO: loghandler

    screendump:   If True, all lines dumped to the logfile will also
                  appear on the screen (stderr).

                  DEFAULTS TO: False

    formatter:    A string which is passed TO the Python logging
                  formatter object.

                  DEFAULTS TO:
                  '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    create_paths: If True, an attempt to change the logfile to a
                  directory/fle path that does not exist will cause
                  the loghandler object to silently create the path and
                  filename.

                  DEFAULTS TO: True

    logfile:      The FUL PATH (fully qualified path and fielname) where
                  log data will be written to disk. If a file name only
                  is given, the existing path of the calling applicaiton
                  is used AFTER being converted to the fully qualified
                  path.

                  DEFAULTS TO: ./loghandler.log

    log_level: The logging object's "log level" as defined by the Python
               "logging" module. This sets the level of message that is actually
               passed to the logger to be included in the logfile.

               Can be passed as a number between 0 and 50.

               Can be passed as one of the following strings:
                 critical
                 error
                 warning
                 info
                 debug

               DEFAULTS TO: 40 (ERROR)

    instantiate: Used noly by the 'log' class above. A call to SetLogger with
                 instantiate=False means either the existing SetLogger object
                 OR NONE will be returned. This is intended to test for the
                 existance of an object.

                 DEFAULTS TO: True

    :METHODS:
        :Name:
            change(param, value)
        :Description:
            Alters the loghandler object's persistent parameters including:
                app_name
                log_level
                screendump
                formatter
                create_paths
                logfile

            These changes are made in the existing, singleton object and IS
            USED BY THE INTERNAL WORKINGS OF LOGHANDLER AND CONFIGHANDLER to
            instantiate and modify itself. Any chenges made here should oly
            be completed with an understanding of the impact it may have on
            the larger, supported methods.
        :Parameters:
            param:    The actual, inflexible variable name used internally by
                      the loghanlder class.

            value:    The new value to be assigned to param.

        :Name:
            screendump()
        :Description:
            Will dump the contents of the current logfile to STD_OUT.
        :Parameters:
            None

        :Name:
            purge()
        :Description:
            Will erase the contents of the existing logfile, with a post-erase
            marker to identify that an erase has been performed.
        :Parameters:
            None

    :RETURNS:
        None. Used as classmethods.

    :USAGE:
        The loghandler.SetLogger  object is used ONLY by the 'log' class above.
        logger = SetLogger(
                            app_name     = app_name,
                            logfile      = logfile,
                            log_level    = log_level,
                            screendump   = screendump,
                            formatter    = formatter,
                            create_paths = create_paths,
                            instantiate  = True # MUST BE TRUE to create object
                           )

        def childMethod(self, var = None):
            log.info("I will log to the same file as ParentClass objects.")
            log.info("var was set to " + str(var))
            log.debug("I will only log if PARAM "log_level" was "DEBUG")

    (script.py)
    obj1 = ParentClass()
    obj2 = ChildClass()

    obj1.parentMethod(1)
    obj2.childMethod(2)

    (MyApp.log)
    2014-12-23 15:35:42,510 - MyApp - INFO - I will log to "MyApp.log"")
    2014-12-23 15:35:42,511 - MyApp - INFO - var was set to 1
    2014-12-23 15:35:42,512 - MyApp - INFO - I will log to the same file
                                             as ParentClass objects.
    2014-12-23 15:35:42,513 - MyApp - INFO - var was set to 2
    """
    # CAN PROBABLY GET RID OF ALL THIS UNCHANGED SHIT ########################################
    __exists = False

    def __new__(cls,
                app_name     = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                logfile      = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                log_level    = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                screendump   = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                format       = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                create_paths = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                migrate      = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                instantiate  = True # DO NOT CHANGE FROM True
                ):
        """
        This is a singleton class.

        The __new__ method is called prior to instantiation with __init__.
        If there's already an instance of the class, the existing object is
        returned. If it doesn't exist, a new object is instantiated with
        the __init__.
        """

        #============= FOR DEBUGGING ===========================================
        # try: #333
        #     print cls.instance,'============'
        #     print datetime.datetime.now().time()
        #     print cls.instance.create_time 
        # except Exception as e: #333
        #     print 'No instance: ', str(e) #333 
        #=======================================================================
        
        # __init__ is called no matter what, so...
        # If there is NOT an instance, just create an instance
        # This WILL run __init__
        # Do NOT set self.__exists here, since if _-exists == True, __init__ is
        # cancelled (it must still run at the first instantiation)
        if not hasattr(cls, 'instance'):
            if instantiate:
                # Create an instance
                cls.instance = super(SetLogger, cls).__new__(cls)
                cls.instance.checks = Checks()
                # SET INSTANCE DEFUALTS HERE =============================================
                # These must be set or errors will arise. 
                cls.instance._APP_NAME     = 'loghandler'
                cls.instance._LOGFILE      = False
                cls.instance._LOG_LEVEL    = 10
                cls.instance._SCREENDUMP   = False
                cls.instance._FORMAT       = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                cls.instance._CREATE_PATHS = True
                cls.instance.instantiate   = True
                cls.instance._MIGRATE      = True
                cls.instance._FORMATTER    = logging.Formatter(cls.instance.format)
                cls.instance._changed_flag = False
                cls.instance._changed_flag_message = ''

                
                return cls.instance
            
            else:
                return None

        # Else if an instance does exist, set a flag since
        # __init__is called, but flag halts completion (just returns)
        else:
            cls.instance.__exists = True
            return cls.instance

    def __init__(self,
                app_name     = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                logfile      = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                log_level    = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                screendump   = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                format       = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                create_paths = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                migrate      = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                instantiate  = 'UNCHANGED', # DO NOT CHANGE FROM 'UNCHANGED'
                ):

        self.handlers = []
        # CHECK FOR NEW INIT OR CHANGES PARAMS=================================
        
        if ( (app_name      != 'UNCHANGED') or (self.__exists is False) ): self.app_name = app_name
        if ( (log_level     != 'UNCHANGED') or (self.__exists is False) ): self.log_level = log_level
        if ( (screendump    != 'UNCHANGED') or (self.__exists is False) ): self.screendump = screendump
        if ( (format        != 'UNCHANGED') or (self.__exists is False) ): self.fomat = format
        if ( (create_paths  != 'UNCHANGED') or (self.__exists is False) ): self.create_paths = create_paths
        if ( (logfile       != 'UNCHANGED') or (self.__exists is False) ): self.logfile = logfile
        if ( (migrate       != 'UNCHANGED') or (self.__exists is False) ): self.migrate = migrate

        # The _changed_flag and _changed_flag_message determine if the actual logger is reset
        # Start the log again after changes or instantiation
        # This has to come at the end of all the changes
        if self._changed_flag:
            # Reset the logging process 
            self._set_logger()
            # Turn off flag
            self._changed_flag = False
            # Send change message to logger directly to avoid loop
            self.logger.info(self._changed_flag_message)
            # Reset changed message
            self._changed_flag_message = ''

        self.__exists = True
    """ PROPERTIES ========================================================="""
    @property
    def create_paths(self):
        return self._CREATE_PATHS
    
    @create_paths.setter
    def create_paths(self, value):
        if value == 'UNCHANGED': return
        _orig = self._CREATE_PATHS
        if isinstance(value, bool): 
            self._CREATE_PATHS = value
            msg = ''.join(["Parameter 'create_path' changed from '", str(_orig), "' -> '", str(self._CREATE_PATHS), "'."])
            try: self.logger.info(msg)
            except AttributeError as e: pass # Silence if logger net yet set, initialization
        else:
            err = ''.join(["LogHandler.SetLogger.create_paths.setter: ", "Value for 'create_paths' (value=", str(value),  ") must be Boolean."])
            raise ValueError(err)
        
    @create_paths.deleter
    def create_paths(self):
        _orig = self._CREATE_PATHS
        self._CREATE_PATHS = False
        msg = ''.join(["Parameter 'create_path' changed from '", str(_orig), "' -> '", str(self._CREATE_PATHS), "'."])
        self.logger.info(msg)
        
    @property
    def migrate(self):
        """
        MIGRATE IS BROKEN, FIX #333
        """
        return self._MIGRATE
    
    @migrate.setter
    def migrate(self, value):
        """
        MIGRATE IS BROKEN, FIX #333
        """
        
        if value == self._MIGRATE: return
        if value == 'UNCHANGED': return
        _orig = self._MIGRATE
        
        if isinstance(value, bool): 
            self._MIGRATE = value
#             msg = ''.join(["Parameter 'migrate' changed: '", str(_orig), "'->'", str(self._MIGRATE), "'. "])
#             self.logger.info(msg)

        else:
            err = ''.join(["LogHandler.SetLogger.migrate.setter: ", "Value for 'migrate' (value=", str(value),  ") must be Boolean."])
            raise ValueError(err)
        
    @migrate.deleter
    def migrate(self):
        """
        MIGRATE IS BROKEN, FIX #333
        """
        
        _orig = self._MIGRATE
        self._MIGRATE = False
#         msg = ''.join(["Parameter 'migrate' changed: '", str(_orig), "'->'", str(self._MIGRATE), "'. "])
#         self.logger.info(msg)
        
    @property
    def logfile(self):
        try:
            return self._LOGFILE
        except (AttributeError, NameError) as e:
            return False
    
    @logfile.setter
    def logfile(self, value):
        """"""
        # The logfile should be the full path and end as a filname
        value = str(value)
        # Set current value for reference
        _orig = self._LOGFILE
        # Strip and set to lower case just for "unchanged" test
        _test = ''.join(c for c in str(value) if not re.match("\s", c)).lower()
        # If the passed in value is the same as the current logfile, just return
        if ( (value == self._LOGFILE) or (_test == 'unchanged') ): 
            return
        # Sets logfile to the syslog or os default
        if ( 
            (_test == 'syslog') or 
            (_test == 'system') or
            (_test == 'os') 
             ):
            self._LOGFILE = 'syslog'
            self._set_change_flag('logfile', _orig, self._LOGFILE)
            return 
        # If none, void or false passed in...set null logfile (no logfile output)
        if (
            (len(_test) < 2)   or # 2 because the shortest valid path is '/a' 
            (_test == 'none')  or
            (_test == 'void')  or
            (_test == 'false') 
            ): 
            self._LOGFILE = False
            self._set_change_flag('logfile', _orig, self._LOGFILE)
            return 
        # If 'stdout' set to only dump to screen
        if re.match('^(sys\.)*st(an)*d(ard)*\s*out[put]*\s*$', _test):
            self._LOGFILE = 'stdout'
            self._set_change_flag('logfile', _orig, self._LOGFILE)
            return
        # If here, value = a filepath. Verify if exists (or create) and continue
        if not self.checks.fullPathExists(path = value, trailing = False, create = self.create_paths, file = True):
            err = ''.join(["LogHandler.setlogger.logfile.setter:", "The logfile path (value='", str(value), "') is not a full path, does not exist, or can not be created (create='", str(self.create_paths), "').", "\n The parameter 'logfile' must be a full path. Set 'create' to 'True' to create the logfile directory if it does not exist. "])
            raise ValueError(err)
        # If here, value is a valid path...so just set it
        self._LOGFILE = value
        self._set_change_flag('logfile', _orig, self._LOGFILE)
        # This migrates all the existing logfile entries to the new log
        # Prevents using the log setting to cover haxor tracks
        if ( (self._MIGRATE) and (self._LOGFILE) ): 
            if self._migrate_log_data(self._LOGFILE, create_paths = self.create_paths):
                msg = ''.join(["\nLogfile migrated from '", str(_orig), "' to '", self._LOGFILE, "'. " ])
                self._changed_flag_message += msg 
            else:
                msg = ''.join(["Unable to migrate Logfile. ", "Previous logfile exists at '", str(_orig), "'. " ])
                self._changed_flag_message += msg 

    @logfile.deleter
    def logfile(self):
        self._LOGFILE = False
    
    @property
    def app_name(self):
        return self._APP_NAME
    
    @app_name.setter
    def app_name(self, value):
        """"""
        if value == self.app_name: return # Does not flip changed flag  
        _orig = self.app_name
#         self.app_name   = self._check_app_name(app_name)
        value = (''.join(c for c in str(value) if re.match("[a-zA-z0-9]", c)))
        self._APP_NAME = value
        # remove all the loggers. The chqnged flag will reset them
#         self._remove_all_loggers()
#         self._changed_flag = True #self._set_logger()
        self._set_change_flag('app_name', _orig, self._APP_NAME)
        
    @app_name.deleter
    def app_name(self):
        self._APP_NAME = 'loghandler' #Default

    @property
    def log_level(self):
        return self._LOG_LEVEL
    
    @log_level.setter
    def log_level(self, value):
        """"""
        DEFAULT_LOG_LEVEL = 40
        MAX_LOG_LEVEL     = 50
        MIN_LOG_LEVEL     = 0
        
        if  value == self.log_level: return # Does not flip changed flag
        _orig = self.log_level
        # Check logging level passed in
        # Check for text string
        if "C" in str(value).upper()[:1]:  self._LOG_LEVEL = 50 #CRITICAL
        if "E" in str(value).upper()[:1]:  self._LOG_LEVEL = 40 # ERROR, Default
        if "W" in str(value).upper()[:1]:  self._LOG_LEVEL = 30 # WARNING
        if "I" in str(value).upper()[:1]:  self._LOG_LEVEL = 20 # INFO
        if "D" in str(value).upper()[:1]:  self._LOG_LEVEL = 10 # DEBUG
        if "NO" in str(value).upper()[:1]: self._LOG_LEVEL = 0  # No logging
        # If here, log_level is either numerical or invalid
        # Strip to only numeric
        value = (''.join(c for c in str(value) if re.match("[0-9]", c)))
        try: value = int(value)
        except ValueError as e: value = DEFAULT_LOG_LEVEL # default
        
        if value < MIN_LOG_LEVEL : self._LOG_LEVEL = MIN_LOG_LEVEL
        if value > MAX_LOG_LEVEL : self._LOG_LEVEL = MAX_LOG_LEVEL
        # Do the change 
        self._LOG_LEVEL = value
        self._set_change_flag('log_level', _orig, self._LOG_LEVEL)
        
    @log_level.deleter
    def log_level(self):
        _orig = self._LOG_LEVEL
        self._LOG_LEVEL = 0 #OFF
        self._set_change_flag('log_level', _orig, self._LOG_LEVEL)

    @property
    def format(self):
        return self._FORMAT
    
    @format.setter
    def format(self, value):
        """"""
        value = str(value)
        if  value == self._FORMAT: return # Does not flip changed flag
        #######################################################################################
        # put fotmatting checker here!
        # For now we trust
        #######################################################################################
        self._set_change_flag('format', self._FORMAT, value)
        self._FORMAT = value
        self._FORMATTER = logging.Formatter(value) # Calls format setter
        
    @format.deleter
    def format(self):
        _orig = self._FORMAT
        self._FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' #Default
        self._FORMATTER = logging.Formatter(self._FORMAT) # Calls format setter
        self._set_change_flag('format', _orig, self._FORMATTER)

    @property
    def screendump(self):
        return self._SCREENDUMP

    @screendump.setter
    def screendump(self, value):
        if  ( (value == self.screendump) or (value == 'UNCHANGED') ): return # Does not flip changed flag
        _orig = self.screendump
#         self.screendump = self._check_screendump(screendump)
        if not isinstance(value, bool):
            err = ''.join(["loghandler.screendump: ", "Parameter 'screendump' (value='", str(value), "') must be boolean."])
            raise ValueError(err)
        self._SCREENDUMP = value
#         msg = ''.join(["screendump: '", str(orig), "'->'", str(self.screendump), "'. "])
#         self._changed_flag_message += msg # self.logger.info(msg)
        self._set_change_flag('screendump', _orig, value)
    
    @screendump.deleter
    def screendump(self):
        _orig = self._SCREENDUMP
        _new = False  # OFF
        self.screendump = _new # OFF
        self._set_change_flag('screendump', _orig, _new)
    """ OVERRIDES==========================================================="""

    def critical(self, message, *args, **kwargs): # OVERRIDES_________________
        if (self.logfile or self.screendump): return self.logger.critical(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        if (self.logfile or self.screendump): return self.logger.error(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        if (self.logfile or self.screendump): return self.logger.warning(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        if (self.logfile or self.screendump): return self.logger.info(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        if (self.logfile or self.screendump): return self.logger.debug(message, *args, **kwargs)

    """ (PRIVATE) GENERAL METHODS==========================================="""
    def _isExistingHandler(self, path):
        """"""
#         if re.match("^(\s){0,}(<){0,1}stderr(>){0,1}(\s){0,}$", str(path).lower()):
        if 'stderr' in str(path).lower():
            path = "<stderr>"
#         else:
#             path = self._check_logfile(path) # returns full path

        try:
            for handler in self.logger.handlers:
                try:
                    if handler.__dict__['stream'].name == path: return True
                except KeyError as e:
                    return False
        except AttributeError as e:
            return False

    def _isExistingLogger(self, app_name):
        """"""
        try:
            if app_name in str(logging.Logger.manager.loggerDict.keys()):
                return True
            else:
                return False

        except Exception as e:
            return False

    def _migrate_log_data(self,
                     dest,
                     source = None,
                     create_paths = None):
        """
        Private method.

        _migrate_log_data(self, source = None, dest = None)

        "source" and "dest" MUST be the full log file path with file name
        and extension I.e. "/der12/dr2/filename.log"
        """
        # If source is None, then source is existing path
        if source is None: source = self._LOGFILE

        # Format the destination
#         dest = self._check_logfile(dest)

        # If source and dest are identical, just return
        if source == dest: return True
        try:
            self.logger.info(''.join(["Moving '", source, "' to '", dest, "'. " ]))
        # If the logger has not yet been set, skip. 
        # Only pass if AttributeError
        except AttributeError as e:
            pass

        # If create_paths is not passed, use the object's current setting
        if create_paths is None:
            try:
                create_paths = self.create_paths
            except (NameError, AttributeError):
                create_paths = True # Assume True if unknown

        # Raises error if None or ""
        err = ''.join(['loghandler._migrate_log_data: ',
                       'Destination parameter (',
                       str(dest),
                       ') is invalid.'])
        # Raises ValueError if dest < 1 or len(dest) chokes
        try:
            if len(dest) < 1: raise ValueError
        except Exception as e:
            try:
                self.logger.error(err)
            except AttributeError as e:
                pass
            return False
#             raise type(e)(err + ' (' + e.message + ')')

        # Check the dir is already there
        if not pathExists(dest, create = create_paths):
#             if create_paths:
#                 os.mkdir(os.path.dirname(dest))
#             else:
                err = ''.join(['loghandler._migrate_log_data: ', "Destination parameter ('", str(dest), "') does not exist. Settings prevent creation."])
                self.logger.error(err)
                return False
#                 raise AttributeError(err)

        try:
            with open(source, "r", 0) as IN:
                with open(dest, "a+", 0) as OUT:
                    for line in IN: OUT.write(line)

            if not fileExists(dest):
                raise Exception

        except Exception as e:
            err = ''.join(["Unable to complete log migration from '",
                           str(source),
                           "' to '",
                           str(dest),
                           "'. Retaining original log file. "
                           ])
            return False

        # Upon success, set self.logfile to new path
#         self.logfile = dest
#         self.log_path = os.path.dirname(dest)
#         self.logfile  = os.path.basename(dest)
        if not self._remove_file(source):
            err = ''.join(["Unable to remove original log file '",
                           str(source),
                           "'. Retaining."])
            self.logger.error(err)

        return True

    def _read(self):
        """"""
        _list = open(self._LOGFILE, "r", 0).read().splitlines()
        return _list


    # === (PRIVATE) ALL _remove METHODS=========================================

    def _remove_all_loggers(self):
        keys = [logging.Logger.manager.loggerDict.keys()]
        for key in keys:
            self._remove_logger(key)

    def _remove_handler(self, handle = None):
        """"""
        try:
            for h in list(logging.Logger.manager.loggerDict[self.app_name].handlers):
                try:
                    if h.__dict__['stream'].name == handle:
                        logging.Logger.manager.loggerDict[self.app_name].removeHandler(h)
                except KeyError as e:
                    pass
        except KeyError as e:
            pass 

    def _remove_file(self, _file):
        try:
            os.remove(_file)
            return True
        except Exception:
            return False

    def _remove_logger(self, app_name):
        try:
            del logging.Logger.manager.loggerDict[app_name]
        except Exception as e:
            pass # Make this more specific later

    def _override_params(self, kwargs):
        pass
    
    def _set_change_flag(self, parameter, original, new):
        self._changed_flag = True #self._set_logger()
        msg = ''.join(["Parameter '", parameter, "' changed: '", str(original), "'->'", str(new), "'. "])
        self._changed_flag = True
        self._changed_flag_message += msg # self.logger.info(msg)
        
    def _set_filehandler(self):
        """"""
        # Logfile
#         logfile = self._check_logfile(logfile) # returns full path
        # If False (no logfile) skip
        if self.logfile is False: return
        elif (self.logfile == 'syslog'):
            # Apple made 10.5 more secure by disabling network syslog:
            if "darwin" in sys.platform.lower(): _path = "/var/run/syslog"
            
            elif 'linux' in sys.platform.lower():
                if   os.path.isfile("/var/log/syslog")  : _path = "/var/log/syslog"
                elif os.path.isfile("/var/log/messages"): _path = "/var/log/messages"
                elif os.path.isfile("/dev/log")         : _path = "/dev/log"
                else                                    : _path = ('localhost', 514) 

            else:
                err = ''.join([self.__class__.__name__, ".", inspect.stack()[0][3], ": ", "loghandler is not yet set to handle other than Linux and OSX logging. " ])
                raise NotImplementedError(err)
#             fh = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON, address=_path)    
            fh = logging.handlers.SysLogHandler(_path, facility='user')

        elif (self.logfile == 'stdout'): fh = logging.StreamHandler(sys.stdout)
            
        else: fh = logging.FileHandler(self.logfile)

#         #Level
#         level = self._check_log_level(level)
#         fh.setLevel(logging.DEBUG)
# #         fh.setLevel(level)

        # Format
#         formatter = self._check_formatter(formatter)
        fh.setFormatter(self._FORMATTER)

        if not self._isExistingHandler(self.logfile):
            self.logger.addHandler(fh)
            msg = ''.join(["Added filehandler '", str(self.logfile), "'."])
            self.logger.info(msg)
            self.handlers.append(fh) #333 aybe dont need this
        else:
            msg = ''.join(["Filehandler '", str(self.logfile), "' already exists. Skipping."])
            self.logger.info(msg)

    def _set_logger(self):
        """
        ALL the 'self' variables need to be set at this point, or this
        will FAIL.
        """
        # Get rid of existing
        self._remove_all_loggers()
        # Create the logger agent
#         self.app_name = 'Testestesteste'
        self.logger = logging.getLogger(self.app_name)

        # Set the logger defaul level
#         level = self._check_log_level(self.log_level)
        self.logger.setLevel(level=self.log_level)
#         self.logger.setLevel(logging.DEBUG)

        # Set the base handlers
        self._set_screendump()
        self._set_filehandler()

#     def _set_screendump(self, screendump = None, level = None, formatter = None):

    def _set_screendump(self):
        """"""
#         self.screendump = self._check_screendump(screendump)
        # If a boolean is passed, reset self.screendump to new setting
        # Otherwise use system defaut
        if self.screendump: #True
            if self._isExistingHandler('stderr'):
                msg = "Screendump is already set to 'True'"
                self.logger.info(msg)
            else:
                # handler object
                ch = logging.StreamHandler()

                #Level
#                 level = self._check_log_level(level)
                ch.setLevel(level=self.log_level)

                # Format
#                 formatter = self._check_formatter(formatter)
                ch.setFormatter(self._FORMATTER)

                #Set
                self.logger.addHandler(ch)
                self.handlers.append(ch) #333 maybe dont need this

                msg = ''.join(["Added screenhandler ", '(logger.stream to <stderr>).'])
                self.logger.info(msg)

        else:
            if self._isExistingHandler('stderr'):
                msg = "Turning off Screendump"
                self.logger.info(msg)
                self._remove_handler('stderr')

                msg = ''.join(["Removed screenhandler ",
                               '(logger.stream to <stderr>).'])
                self.logger.info(msg)


if __name__ == '__main__':
    import time
    log.debug(
              ' Dateien angefügt', 
              app_name = "test", 
              log_level = 10, 
              logfile = 'stdout', 
              screendump = False
              )

    
#===============================================================================
#     print '--------------------'
#     print 'Doing null test. nothing should log from this.'
#     log.debug('This is a null test, nothing should print anywhere.')
#     
#     print '--------------------'
#     # Set logger manually
#     print 'Starting logger parameters for first time (New parameters)'
#     log.info('Sending first call of loghandler...',
#              app_name   = 'loghandlertest1',
#              logfile    = '/Users/mikes/Documents/Eclipseworkspace/BioCom/BioComCode/common/tmpdirforlog/logfiletest1.log',
#              log_level  = 10,
#              screendump = True, 
#              create_paths = True
#              )       
#  
#     print '--------------------'
#     print 'Starting logger parameters for second time (New parameters)'
#     log.info('Sending second call of loghandler...',
#              app_name   = 'loghandlertest2',
#              logfile    = '/Users/mikes/Documents/Eclipseworkspace/BioCom/BioComCode/common/tmpdirforlog/logfiletest2',
#              log_level  = 10,
#              screendump = True, 
#              create_paths = True
#              )    
# 
#     print '--------------------'
#     print 'Check parameter changes....'
#     print '--------------------'
#     print 'Changing screendump to False...'
#     log.info('Changing screendump to False...',
#              screendump = False,
#              ) 
#              
#     print '--------------------'
#     print 'Changing screendump back to True...'
#     log.info('Changing screendump back to True...',
#              screendump = True,
#              ) 
#     
#     print '--------------------'
#     print 'Changing format ...'
#     log.info('Changing format and formatter...',
#              format = '%(asctime)s - %(levelname)s - %(message)s',
#              ) 
# 
#     print '--------------------'
#     print 'Changing format back...'
#     log.info('Changing format and formatter...',
#              format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#              ) 
#     
#     print '--------------------'
#     print 'Changing APP_NAME ...'
#     log.info('Changing app_name...',
#              app_name = 'newapp',
#              ) 
# 
#     print '--------------------'
#     print 'Changing LOG_LEVEL to 20 ...'
#     log.info('Changing LOG_LEVEL to 20 ...',
#              log_level = 20,
#              ) 
#  
#     print '--------------------'
#     print 'Changing LOG_LEVEL back to 10 ...'
#     log.info('Changing LOG_LEVEL back to 10 ...',
#              log_level = 10,
#              ) 
# 
# # MIGRATE IS BROKEN FIX LATER ===================================================
# #     print '--------------------'
# #     print 'Changing migrate to False ...'
# #     log.info('Changing migrate to False ...',
# #              migrate = False,
# #              ) 
# # 
# #     print '--------------------'
# #     print 'Changing migrate back to True ...'
# #     log.info('Changing migrate back to True ...',
# #              migrate = True,
# #              ) 
# #===============================================================================
# 
#     print '--------------------'
#     print 'Changing create_path to False ...'
#     log.info('Changing create_path to False ...',
#              create_paths = False,
#              ) 
#     print '--------------------'
#     print 'Changing create_path back to True ...'
#     log.info('Changing create_path back to True ...',
#              create_paths = True,
#              ) 
#     
# #     print '--------------------'
# #     print 'Starting logger parameters for third time (NOTHING CHANGED)'
# #     log.info('Sending third call of loghandler...',
# #              app_name   = 'loghandlertest2',
# #              logfile    = './logfiletest2',
# #              log_level  = 10,
# #              screendump = True, 
# #              create_paths = True
# #              )        
#     
# #     print '--------------------'
# #     print 'Sending final unchanged  call of loghandler (NO CHANGES PASSED)'
# #     log.info('Sending final unchanged  call of loghandler (NO CHANGES PASSED)')
#===============================================================================
