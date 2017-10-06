
##############################################################################
##############################################################################
#        confighandler NEEEDS TO BE UPDATED FOR PY3. DO NOT USE YET          #
##############################################################################
##############################################################################


##############################################################################
# Removal of the "__license__" line or content from  "__license__", or removal
# of "__author__" in this or any constituent # component or file constitutes a
# violation of the licensing and copyright agreement.
__author__      = "Mike Rightmire"
__copyright__   = "BioCom Software"
__license__     = "PERPETUAL_AND_UNLIMITED_LICENSING_TO_THE_CLIENT"
__version__     = "0.9.10.0"
__maintainer__  = "Mike Rightmire"
__email__       = "Mike.Rightmire@BiocomSoftware.com"
__status__      = "Development"
##############################################################################

from common.checks import Checks
checks = Checks()
_slash = checks.directory_deliminator()

from configparser   import SafeConfigParser
from common.loghandler     import log

import ast
import configparser
import inspect
import os
import re
import sys
import time
import traceback
import types


class Callobj(object):
    """
    This is a null object for when ConfigHandler is not called from a
    Class Object
    """
    def __init__(self):
        self._config = None
        
        
class ConfigHandler(object):
    """
    :NAME:
        ConfigHandler(config_file = '/path/path/filename.conf',
                      [global=True/False],
                      [app_name   = "MyApp"],
                      [logfile    = "/path/path/MyAppLog.log"],
                      [log_level  = <int>],
                      [screendump = True/False],
                      [config_file = "/path/path/MyApp.conf"],
                      [pidfile = "/var/run/MyApp.pid"],
                    )

    :DESCRIPTION:
        ConfigHandler() is a 'suite' configuration handler. It is intended to be
        called by a class's "__init__" and set the configuration parameters
        throughout an entire software package (I.e. the same configuration
        information for every class object that is instantiated in association
        with a complete piece of functional software).

        The primary goal with ConfigHandler is to load a single, consistent
        configuration environment to be passed amongst ALL objects within a
        package.

        ConfigHandler is a SINGLETON, meaning once instantiated, THE SAME OBJECT
        will be returned to every class object calling it.

        ConfigHandler ALSO INITIATES the "loghandler"  (which is ALSO  a
        singleton and ALSO intended to be a consistent single logging object
        passed amongst all instantiated objects of a package.

        IF YOU CALL ConfigHandler, YOU DO NOT NEED TO SET THE LOGGER, however
        doing so will not break anything.


    :ARGUMENTS:
        config_file:    <full path with filename>

            MANDATORY

            Tell ConfigHandler where to find the configuration file.

            If the file does not exist, error is raised.

            The default config file example has the details about
            creating a config file. It is based on Python's ConfigParser
            module and uses that format.

            I.e.

            parameter = string

            While ConfigHandler also handles the logging module, if
            a config file is not desired, just use the 'loghandler.log'
            @classmethod to manually instantiate the logger (see
            LogHandler's help page for details.

            I.e.

            from loghandler import log

            log.info(
                "I automatically instantiate the logging object.",
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


        global:     True/False

            OPTIONAL

            True inserts the config file's parameter definitions into
            'callobj' (the object calling confighandler) AS WELL AS
            the confighandler object that's getting returned.

            DEFAULTS TO: True

        app_name   = <str>

            OPTIONAL

            Sets the 'app_name' variable for the LogHandler. See the
            LogHandler help or 'loghandler.py' for details.

        logfile    <full path with filename>

            OPTIONAL

            Sets the 'logfile' variable for the LogHandler. See the
            LogHandler help or 'loghandler.py' for details.

        log_level  = <int>

            OPTIONAL

            Sets the 'log_level' variable for the LogHandler. See the
            LogHandler help or 'loghandler.py' for details.

        screendump = True/False

            OPTIONAL

            Sets the 'screendump' variable for the LogHandler. See the
            LogHandler help or 'loghandler.py' for details.


        *args, **kwargs:
            Numerous parameters can be passed into the ConfigHandler object.

            Using args/kwargs for even the one mandatory parameter was chosen
            to allow for future flexibility.


    :VARIABLES:
        No userspace mutable variables.

    :METHODS:
        set(varname, value, default = None):
            Same end result as 'config.var = value', however useful with 
            scriptbound variables. 
            
            I.e.
            config = ConfigHandler(config_file = '/path/path/filename.conf')
            kwargs = {'var1':'1, 'var2':2}
            for i in kwargs:
                config.set(i, kwargs[i]) 
            print config.var1
            print config.var1
            
        get(self, varname, default = None)            
            Same end result as 'x = config.var', however useful with 
            scriptbound variables.
            
            I.e. 
            config = ConfigHandler(config_file = '/path/path/filename.conf')
            list = ['var1', var2']
            for i in list:
                print config.get(i) 

    :RETURNS:
        self as callingobject._config

    :USAGE:
        <myClass>
            def __init__(self):
                self.config_var = ConfigHandler(config_file = "./my.conf)

    :EXAMPLE:
        <configuration.conf>
        # ---------------------------------------------------------------------
        # Class configuration file
        # ---------------------------------------------------------------------
        #######################################################################
        #  THIS FILE SHOULD ONLY BE USED TO SET SIMPLE CONFIGURATION VALUES.
        # NOT AS A REPLACEMENT FOR SETTING VARIABLES PROPERLY WITHIN A CLASS!!
        #
        # THE PARAMETERS SET BY CONFIGHANDLER USING THIS FILE ARE SET DIRECTLY
        # IN THE CALLING CLASS'S "self". PLEASE BE AWARE WHEN CREATING THIS
        # CONFIG FILE
        #######################################################################
        #
        #  I.e. The line "option = 1" in this file creates
        #       "callingobject.self.option = 1"
        #       AND
        #       "callingobject.self._config.option = 1".
        #
        #  class some_python_class(object):
        #    def __init__(self):
        #      ConfigHandler(self, config_file = "/dir/dir/file.conf")
        #
        #  print self.option
        #  1
        #
        #  print self._config.option
        #  1
        #
        # SECTIONS:
        #  Each [SECTION] defines a specific set of option-value pairs. The
        # SECTION name is userspace and arbitrary.
        #
        # OPTIONS:
        #  option=value
        #   Each option within a section will create a variable BY THE SAME
        #   NAME AS THE 'OPTION' in the instantiated ConfigHandler OBJECT with
        # its value set to "value".
        # I.e.
        #  "name=Hydrogen" creates a variable called "self.name" in the
        #  ConfigHandler object with the value of "Hydrogen".
        #  This is the same as if the line of code 'self.name = str("Hydrogen")'
        #  had been written directly into the calling objects code.
        #
        #   Caveats:
        #     - Spaces after the "=" are ignored.
        #
        #     - ALL VALUES ARE A STRING...so they MAY have to be converted for
        #       use. At instantiation, ConfigHandler attempts to convert floats,
        #       integers and boolean - but be prepared to check for this.
        #
        #     - Numbers will be returned as floats or int...never bools.
        #
        #     - Quotes around values will be returned as part of the string.
        #
        #
        # FORMAT:
        #  [section_name]
        #    option=value
        #
        #  - Lines starting with "#" are ignored.
        #
        #  - Lines with "#" AFTER DATA ARE *NOT* IGNORED.
        #    I.e. name=Hydrogen # This comment will be included in name's value
        #
        #  - Do NOT use quotes for text values.
        # ---------------------------------------------------------------------
        [LOGGING]
        logfile             = MyPackage.log
        log_path            = /shared/MyPackage/var/log/
        app_name            = MyPackageName
        log_level           = 10
        screendump          = True
        create_paths        = True
    """
    __exists = False

    def __new__(cls, 
                 config_file = False, # Param so it can be passed in blind 
                *args, **kwargs):
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

        if not hasattr(cls, 'instance'):
            # Removing the error to allow for a non-configured object.
            # On first initialization, need to check and remove errors is
            # config file does not exist, or logfile is not set   
            #===================================================================
            # # If ConfigHandler() is called without any arguments, it must either return an EXISTING instance of ConfigHandler or error
            # if len(args) == 0 and len(kwargs) == 0:
            #     err = ''.join(["An instance of class 'ConfigHandler' ", "does not yet exist. Please ensure your code ", "creates a proper instance from a config file ", "before attaching."])
            #     raise EnvironmentError(err)
            #===================================================================
            cls.instance = super(ConfigHandler, cls).__new__(cls)
            # Putting it here causes Checks to only be created once
#             cls.instance.checks = Checks()
            # self.false_on_AttributeError is used in __getattr__. 
            # If 'True', then 'False' is returned when a non-existent atttribute is accessed. 
            # Otherwise an normal AttributeError is raised using Traceback 
            cls.instance.false_on_AttributeError = kwargs.pop('false_on_AttributeError', True)
            return cls.instance

        # Else if an instance does exist, set a flag since
        # __init__is called, but flag halts completion (just returns)
        else:
            cls.instance.__exists = True
            return cls.instance

    def __init__(self, 
                 config_file = False, # Param so it can be passed in blind 
                 *args, **kwargs):
        """"""        
        # Call here to start logging with whats in kwargs
        # DO PASS IN KWARGS here
        self.override_log(kwargs) 
        # Actually creates the loghandler object.
        log.debug('Initiating logger with {K}'.format(K = str(kwargs)), **kwargs)
        log.info("ConfigHandler called with '{F}'".format(F = str(self.config_file)))
#         self.override_log(**kwargs)
        # Singleton. If confighandler object exists, do not re-run __init__,
        if self.__exists:
            # this will defacto Re-run the config file 
            if kwargs.pop('reload', False): self.config_file = self._CONFIG_FILE
            # __init__get run everytime even if singletone. So if exists, return  
            return 
        # **kwargs here passes in loghandler parameers from ConfigHandler instantiation
        try:
            for i in inspect.stack():
                print("i:", i)
            print("self.callobj:", self.callobj)
            self.callobj = inspect.currentframe().f_back.f_locals['self']
            stack0 = inspect.stack()[0]
            print("inspect.getmembers(stack0):", inspect.getmembers(stack0))
            stack1 = inspect.stack()[1]
            print("inspect.getmembers(stack1):", inspect.getmembers(stack1))
#             print('stack[1][0].f_locals["self"]', inspect.stack[1][0].f_locals["self"])
            sys.exit()
            
            
            
            print("inspect.currentframe().f_back.f_locals['self']:", inspect.currentframe().f_back.f_locals['self'])            
#             self.callobj = inspect.currentframe().f_back # Gets teh calling object
            self.callobj = inspect.currentframe().f_back.f_locals['self']
            self.callobj_class = inspect.getmembers(self.callobj)[0]
            print("self.callobj_class=", self.callobj_class) #333
            print("self.callobj.getmembers()=", inspect.getmembers(self.callobj))
            print("calling class=", inspect.getmembers(self.callobj).__class__)
            print("calling __dict__=", inspect.getmembers(self.callobj).__dict__)
            #self.callobj = inspect.stack()[1][0]
#             self.callobj = inspect.stack()[1][0].f_locals['self']
            print("self.callobj =", self.callobj ) #3333
            print("self.callobj.__dict__ =", self.callobj.__dict__ ) #3333

            self.caller_name = sys._current_frames().values()
            for i in self.caller_name: print("i=", i)#333             
            print("sys._current_frames().values()=", sys._current_frames().values()) #333
            self.caller_name = sys._current_frames().values()[0]
            self.caller_name = self.caller_name.f_back.f_globals['__file__']            
            self.caller_name = os.path.basename(self.caller_name)
            self.caller_name = self.caller_name.lower().replace('.py','')
        except KeyError as e:
            log.debug("ConfigHandler was instantiated by a non-class-object. Creating empty placeholder object")
            self.callobj = Callobj()
            self.caller_name = 'UNKNOWN_CALLER'
        # DEFAULT PARAMETERS ARE SET HERE
        # This defacto loads the config file
        self.config_file = config_file
#             log.info("Using config_file: '" + str(self.config_file) + "'.") 
#             self._load_all_from_config_file()
#         else:
#             log.info("NO CONFIG FILE LOADED. CREATING BLANK OBJECT. ('config_file' = False).") 
            
        # Now that we have parsed the config file, use any logging params from the config file
        # DO NOT PASS KWARGS to use settings loaded from config_file!!!
        self.override_log() 

    def __getattr__(self, attr):
        """
        Don't raise AttributError when a variable does not exist. 
        Return 'False' instead
        """
        exc_info = sys.exc_info()
        e = ''
        if self.false_on_AttributeError:
            return False
        else:
            if traceback.print_exception(*exc_info) is not None:
                e = str(traceback.print_exc())
            e = ''.join([e, "name '", attr, "' is not defined"])
            raise NameError(e)
    
    @property
    def config_file(self):
        return self._CONFIG_FILE

    @config_file.setter
    def config_file(self, value):
        """"""
        if value is False: 
            self._CONFIG_FILE = False
            return
        # No change
        elif value == self.config_file: 
            return 
        # Something IS different
        _value = str(value).strip()
        err = "ConfigHandler.config_file.setter: Parameter 'config_file' must be in the format '/dir1/dir2/filename.conf'. (config_file='{V}')".format(V = _value) 
        for p in ["void", "none", "false"]:
            if ( len(_value) < 2 or re.match("^{p}$".format(p = p), _value, re.IGNORECASE) ):
                    self._CONFIG_FILE = False 
                    log.debug("ConfigHandler.config_file.setter: config_file set to 'False'.")
                    return
        # Check config file exists
        if not checks.isFile(_value): #, full = True, relative = False, trailing = False):
            raise ValueError("config_file '{F}' does not appear to exist or is not readable. {E}".format(F = _value, E = err))
        # Set
        self._CONFIG_FILE = _value
        # Load it by default. No time like the present
        self._load_all_from_config_file()

        return
        
    @config_file.deleter
    def config_file(self):
        self._CONFIG_FILE = False
        
#     def _check_config_file(self, kwargs):
#         """"""
# 
#         conf = kwargs.pop('config_file', False)
#         
#         _test = ''.join(c for c in str(conf) if not re.match('\s', c)).lower()
#         if (
#             (len(_test) < 1) or
#             (_test == 'void') or
#             (_test == 'none') or
#             (_test == 'false')
#             ):
#             self.config_file = False 
#             return False
# 
#         if not checks.fullPathCheck(conf):
#             err = ''.join(["Invalid 'config_file' parameter set as '", str(conf),"'. ", "Configuration file name MUST be a fully qualified path passed ", "as a string."])
#             raise ValueError(err)
# 
#         #=======================================================================
#         # # Eventually use self.caller_name to search  for config file automaticly
#         # if (conf is None):
#         #     log.error("Cannot find config file " + str(conf))
#         #     raise ValueError(err)
#         #=======================================================================
# 
# #         conf = str(conf).replace(' ', '\ ')
# 
#         if (not checks.fileExists(conf) ):
#             log.error("Config file at '" + str(conf) + "Cannot be opened.")
#             raise ValueError(err)
# 
#         self.config_file = conf
#         return conf
        
    def _load_all_from_config_file(self):
        """"""
        self._open_file()
        self.loadattr()
#         # Override config file vars.
#         # This overwrites variables set from the config file, with any identical
#         # variables that were passed into the __init__. This way, config file
#         # params can be selectively overrided at runtime.
#         # This needs to come AFTER loding the config
#         # file but BEFORE the final SetLogger to allow for config file vars
#         # to be manually overidden
#         # Always send dict(kwargs)
#         self.override(dict(kwargs))

        # Should th following mandatory parameters not exist in the config
        # file AND not have been passed to the __init__, create them here
        # using set defauls
#         self._set_mandatory_defaults(self.MANDATORY_DEFAUTS)

#     def _set_mandatory_defaults(self, _dict):
#         """
#         """
#         for key in _dict.keys():
#             if key not in self.__dict__.keys():
#                 self.__dict__[key] = _dict[key]
#         return

    def _open_file(self):
        self.config = SafeConfigParser()
        self.config.optionxform = str
        # This will return false if config_file is not set. Otherwise error will be raised
        try:
            if self.config_file:
                self.config.read(self.config_file)
        except AttributeError as e:
            return False
        
        return True
    
#     def _set_parameters(self, kwargs):
#         ### These params check for loghandler object params
#         # Get params from kwargs or set to default
#         # self.paramname  = kwargs.pop("paramname", default_value)
#         # These should all set 'self' parameters
#         create_paths    = kwargs.pop("create_paths", False)
#         self.create_paths = self._check_create_paths(create_paths)
# 
#         log_level       = kwargs.pop("log_level", 40)
#         self.log_level = self._check_log_level(log_level)
# 
#         screendump      = kwargs.pop("screendump", False)
#         self.screendump = self._check_screendump(screendump)
# 
#         self.GLOBAL          = kwargs.pop("global", True)
# 
#         app_name        = kwargs.pop("app_name", "configparser")
#         self.app_name = self._check_app_name(app_name)
# 
#         logfile         = kwargs.pop("logfile", "./configparser.log")
#         self.logfile = self._check_logfile(logfile)

    def get(self, varname, default = None):
        """
        Retrieves the attribute from ConfigHandlers "self"
        """
        # If the first attempt to return a self var fails, control
        # should pass to @handlertry where corrections can be set
        # For now this is just a passthrough, which will drop control
        # to the second line, which returns the default
        try:
            return self.__dict__[varname]
        except KeyError as e:
            return default

    def set(self, varname, value, default = None):
        """
        Sets an attribute from ConfigHandlers "self"
        """
        self.__dict__[str(varname)] = value
        return True

    def delete(self, varname):
        try:
            # Delete to param.deleter 
            del vars()[varname]
        except:
            # If fails set to False
            vars()[varname] = False
        
    def load(self, config_file, *args, **kwargs):
        log.debug("ConfigHandler.load: Loading '{F}'".format(F = str(config_file))) 
        self.config_file = config_file
#         self._load_all_from_config_file(**kwargs)
        
    def loadattr(self, varname = None, section = None):
        """
        Retrieves a variable from the CONFIG FILE (not self)
        """
        # This searched only the configparser object created from the config_file
        # If config_file is False, just return. There is nothing to search
        if self.config_file: # Anything other than False
            for section_name in self.config.sections():
    
                if ((section_name.lower() == str(section).lower()) or
                    (section is None)):
    
                    # ConfigParser.InterpolationMissingOptionError as handlertry error message
                    for name, value in self.config.items(section_name):
    
                        if ({"LOADALL":True, None:True, name:True}.get(varname)):
                            value = self.stringToLiteral(value)
                            self.__dict__[name] = value # SETS the value to the config object
    #===========================================================================
    #                         if varname is not None: 
    #                             return value
    # 
    #     # If here, nothing was found in config_file or config_file not set
    #     err = ''.join(["Unable to find variable '", str(varname), "' in section '", str(section), "' in config_file '", str(self.config_file), "'. " ])
    #     log.error(err)
    #     return None
    #===========================================================================
        
    def override(self, *args, **kwargs):
        """
        :NAME:
            ConfigHandler.override(*args, **kwargs)
        
        :DESCRIPTION:
           This method is used to override multiple parameters within the 
           instantiated ConfigHandler object. Is more useful that 
           ConfigHandler.set(param, vale) for large volumes of changes or 
           when a class method associated with a ConfigHandler object receives
           overriding **kwargs and wants to propagate those kwargs through the 
           ConfigHandler object. 
           
        :USAGE:
            configobj = ConfigHandler()
            configobj.override({'attribut1':1, 'attribute2':'string'})
            # configobj.attribute1
            1
            # configobj.attribute1
            'string'
            
        """
        #=======================================================================
        # if len(args) > 0:
        #     err = ''.join(["ConfigHandler.override: ", "Does not yet accept non-keyword arguments. ", "\n(args = '", str(args), "'\nkwargs='", str(kwargs), "'."])
        #     raise NotImplementedError(err)
        #=======================================================================
#         if len(kwargs) > 0: return self._override_with_kw_vars(kwargs) # Returns true or false for success
#         else: return False
        for key in kwargs.keys():
            self.__dict__[key] =  kwargs[key]
        self.override_log()
        return True
        
    #@handlertry("PassThroughException:")

#     def verify_file(self):
#         """"""
#         log.debug(("Verfiying " + str(self.config_file)))
#         # Check config file exists since parser will not error if you
#         # attempt to open a non-existent file
#         if not checks.fileExists(self.config_file):
#             e = ''.join(["ConfigFileNotFound(",
#                          str(self.config_file),"):"])
#             raise IOError(e) # Remove me and active self.err line

    def override_log(self, *args, **kwargs):
        """
        This overrides any parameters in the existing LogHandler object
        The logic is:
        
        - If the ConfigHandler object has a log attribute, it was picked up
          from the config_file, so should override whats in there. 
        
        - Any kwargs passed in should override the stuff in the ConfigHandler
          object.
          
        - If there's no ConfigHandler object attribute AND no kwarg passed in, 
          setting 'UNCHANGED' will be passed to the log object...meaning ignore
          the variable.    
        """
        # List of log params
#         _params = ["app_name", "logfile", "log_level", "screendump", "format", "create_paths", "migrate"]
        # Holder for updated log parameters
#         _log = ''
        _log_kwargs = {}
        # These are the LogHandler object params
        for _param in ["app_name", "logfile", "log_level", "screendump", "format", "create_paths", "migrate"]:
            # Set the log param to the existing log param, if it exists. 
            try: 
                _value = kwargs.pop(_param, False) # Always returns value
                # Set _log_kwargs[_param] to passed in value, or the existing config object parameter
                if _value:
                    _log_kwargs[_param] = _value # Passed to log call
                    vars()[_param]      = _value # Sets to local configHandler object 
            # KeyError if no self.vars()[_param].Pass
            except KeyError: pass # _log_kwargs[_param] = 'UNCHANGED'
        # Now that _log_kwargs is loaded with ONLY pertinent params, 
        ### THE CALL TO LOG.DEBUG IS WHAT ACTUALLY RESETS THE PARAMETERS ######  
        if len(_log_kwargs) > 0: # No params to change
            log.debug("Resetting the following log parameters: {P}".format(P = str(_log_kwargs)), **_log_kwargs)
#         # Change the ConfigHandler values to match
#         for _key, _value in _log_kwargs.iteritems():
#             self.__dict__[_key] = _value 

    def stringToLiteral(self, value):
        """"""
        # Check for boolean text, return actual bool
        if (re.match("^true$",  value.lower())) : return True
        if (re.match("^false$", value.lower())) : return False
 
        # Check for INT (INT MUST come before FLOAT)
        try:                return int(value) # Int MUST come first
        except ValueError:  pass
        # Check for float
        try:                return float(value) # Int MUST come first
        except ValueError:  pass
#         if (re.match("^[0-9]+\.[0-9]*$", value)): return float(value)
#         if (re.match("^[0-9]+$", value)):         return int(value)
        # Check for list and dict
        if (value.startswith('[') or value.startswith('{')): return ast.literal_eval(value)
        # Otherwise just return original string, no conversion
        return value

if __name__ == "__main__":
#     import time
    log.debug( "Starting CUPS-QRNote-backend",
              app_name   = "QRNote",
              logfile    = "syslog",
              log_level  = 10,
              screendump = True,
#               formatter  = '%(asctime)s-%(name)s-%(levelname)s-%(message)s',
              create_paths = True
             )
#     o = ConfigHandler("/Users/mikes/Documents/Eclipseworkspace/Bioproximity/OpenMS-Python-Luigi/site-packages/Bioproximity/etc/Workflow.conf")
    o = ConfigHandler(None)
    print(o.config_file)
    print (o.AWS_ID)
    #===========================================================================
    # o.var1 = 'test'
    # print o.var1
    # time.sleep(.5)
    # print o.var2
    #===========================================================================
     
#===============================================================================
# #     from BiocomCommon.loghandler import log
# #     log.debug( "Starting CUPS-QRNote-backend",
# #               app_name   = "QRNote",
# #               logfile    = "syslog",
# #               log_level  = 10,
# #               screendump = True,
# # #               formatter  = '%(asctime)s-%(name)s-%(levelname)s-%(message)s',
# #               create_paths = True
# #              )
#===============================================================================

#===============================================================================
#     class forttest(object):
#         def __init__(self):
#  
#             self.config = ConfigHandler(
#                     app_name   = "QRNote",
#                     logfile    = "syslog",
#                     log_level  = 10,   # for beta testing
#                     screendump = True,
#                     create_paths = True, 
# #                     config_file = '/Users/mikes/Documents/Eclipseworkspace/BioCom/BioComCode/common/ConfigHandlertest.conf'
# #                     config_file = None
#                                         )
#             self.config._open_file()
#             self.config.loadattr(varname = 'qval', section = 'DEFAUTS')
#     obj = forttest()
#===============================================================================
#     print obj.instantiate_default
#     print obj._config.instantiate_default

#     qrnote = ConfigHandler(
#                     app_name   = "QRNote",
#                     logfile    = "syslog",
#                     log_level  = 10,   # for beta testing
#                     screendump = False,
#                     create_paths = True,
#     )
