#!/usr/local/bin/python3

from common.loghandler import log

log.debug('The first log line can instantiate the variables...', 
          app_name = "MyApp-test", 
          log_level = 10, 
          logfile = 'stdout', 
          )

log.warning("This line works like the normal Python logger")

log.debug("Now I'm changing the logfile...", 
          logfile = './test.log',
          )

        
    
        