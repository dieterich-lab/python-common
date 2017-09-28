# -*- coding: utf-8 -*-

__author__      = "Mike Rightmire"
__copyright__   = "Universitäts Klinikum Heidelberg, Section of Bioinformatics and Systems Cardiology"
__license__     = "Not licensed for private use."
__version__     = "0.9.0.0"
__maintainer__  = "Mike Rightmire"
__email__       = "Michael.Rightmire@uni-heidelberg.de"
__status__      = "Development"

from common.loghandler import log
from dateutil.relativedelta import relativedelta as rd

import re
    
def convert_timestring_input(value, increment = 's'):
    _inc = str(increment)
    _value = str(value) 
    
    if re.search("[^0-9A-Za-z\.]", _value):
        err = "Illegal character found in time string. Only numbers and characters are allowed in the format '1Y2M3d4h5m6s'. Only integers are allowed as numbers. "
        raise ValueError(err)
    
    _value = ''.join(c for c in str(value) if re.match("[0-9A-Za-z]", c))
    _values = re.findall("(\d*\D*)",_value)
    message_to  = ""
    message_from  = ""
    total_seconds = 0
    
    for time in _values:
        if len(time) < 1: continue # Correcting for findall null end
        # Parse by character
        # Get number portion first
        _num = ''.join(c for c in time if re.match("[0-9]", c))
#         try: _num = abs(int(_num)) # No negatives 
        try: _num = abs(float(_num)) # No negatives 
        except ValueError as e:
            err = "Numerical component in time variable does not appear to be a valid integer. (V)".format(V = _value)
            raise ValueError(err)
        # Get the calendar type (Year, day, etc)
        # _cal = ''.join(c for c in _value if re.match("[YyMmDdHhSs]", c))
        # Everything is handled in seconds first
        _cal = ''.join(c for c in time if re.match("[a-zA-Z]", c))    
        if   _cal.lower().startswith("y"): # Year not case sensitive
            if _num > 1: message_from += (str(_num) + " Years, ")
            else:        message_from += (str(_num) + " Year, " )
            total_seconds += (_num * 31536000) 
        
        elif _cal.startswith("M") or _cal.lower().startswith("mo"):
            if _num > 1: message_from += (str(_num) + " Months, ")
            else:        message_from += (str(_num) + " Month, " )
            total_seconds += (_num * 2592000) 
            
        elif _cal.lower().startswith("d"): 
            if _num > 1: message_from += (str(_num) + " Days, ")
            else:        message_from += (str(_num) + " Day, " )
            total_seconds += (_num * 86400) 
            
        elif _cal.startswith("h") or _cal.lower().startswith("ho"): # Hours 
            if _num > 1: message_from += (str(_num) + " Hours, ")
            else:        message_from += (str(_num) + " Hour, " )
            total_seconds += (_num * 3600) 
        
        elif _cal.lower() == "m" or _cal.lower().startswith("mi"):
            if _num > 1: message_from += (str(_num) + " Minutes, ")
            else:        message_from += (str(_num) + " Minute, " )
            total_seconds += (_num * 60) 

        elif _cal.lower().startswith("s") or len(_cal) < 1: # Starts with s or has no characters (assuming seconds)
            if _num > 1: message_from += (str(_num) + " Seconds, ")
            else:        message_from += (str(_num) + " Second, " )
            total_seconds += (_num) 

        elif _cal.startswith("H") or _cal.lower().startswith("hu"): # Human
            err = "Invalid time increment found. 'Human' time increment only valid for output. Valid time increments are Y(ear), M(onth), d(ay), h(our), m(inute), s(econd)"
            raise ValueError(err)
        
        else:
            err = "Invalid time increment found. Valid time increments are Y(ear), M(onth), D(ay), H(our), M(inute), S(econd)"
            raise ValueError(err)
    
    # Once done adding up seconds, convert to desired increment. 
    if   _inc.lower().startswith("y"): # Year not case sensitive
        total_time = (total_seconds / 31536000) 
        if total_time > 1: message_to += (str(total_time) + " Years")
        else:              message_to += (str(total_time) + " Year" )
    
    elif _inc.startswith("M") or _inc.lower().startswith("mo"):
        total_time = (total_seconds / 2592000) 
        if total_time > 1: message_to += (str(total_time) + " Months")
        else:              message_to += (str(total_time) + " Month" )
        
    elif _inc.lower().startswith("d"): 
        total_time = (total_seconds / 86400) 
        if total_time > 1: message_to += (str(total_time) + " Days")
        else:              message_to += (str(total_time) + " Day" )

    elif _inc.startswith("h") or _inc.lower().startswith("ho"): # Hours
        total_time = (total_seconds / 3600) 
        if total_time > 1: message_to += (str(total_time) + " Hours")
        else:              message_to += (str(total_time) + " Hour" )

    elif _inc.lower() == "m" or _inc.lower().startswith("mi"):
        total_time = (total_seconds / 60) 
        if total_time > 1: message_to += (str(total_time) + " Minutes")
        else:              message_to += (str(total_time) + " Minute" )

    elif _inc.lower().startswith("s") or len(_inc) < 1: # Starts with s or has no characters (assuming seconds)
        total_time = (total_seconds) 
        if total_time > 1: message_to += (str(total_time) + " Seconds")
        else:              message_to += (str(total_time) + " Second" )
    
    elif _inc.startswith("H") or _inc.lower().startswith("hu"): # Human 
        # Human readable gets a special exception here, since it returns a string and not a number
        fmt = '{0.days} days {0.hours} hours {0.minutes} minutes {0.seconds} seconds'
        total_time = fmt.format(rd(seconds=total_seconds))
        message = ''.join(["Converted to '", total_time, "' from '", message_from[:len(message_from) - 2], "'."])
#         log.info(message)
        return total_time 

    else:
        err = "Invalid time increment for return value found. Valid time increments are Y(ear), M(onth), D(ay), H(our), M(inute), S(econd)"
        raise ValueError(err)


    message = ''.join(["Converted to '", message_to, "' from '", message_from[:len(message_from) - 2], "'."])
#     log.info(message)    
    
    return round(total_time, 2)

if __name__ == '__main__':
    log.debug("Debugging:", 
              logfile = "system", log_level = 10, screendump = True)
    print(convert_timestring_input("2d", "sec"))