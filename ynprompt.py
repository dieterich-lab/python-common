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

#===============================================================================
# def prompt_message(message): #argument is question, returns boolean answer
#     glob.sys.stdout.write('------------------------------------\n'+message+'\n------------------------------------')
#     answer_bool = strtobool(input('\n[y, yes, t, true, on, 1; false || n, no, f, false, off, 0]\n'))
#     return answer_bool
#===============================================================================

def yn(prompt = "", bool = True, full_yes = True, full_no = False, default = None):
    """
    :NAME:
        yn(prompt [bool, full_word, enter])
        
    :DESCRIPTION:
        'yn' creates a simply "yes/no" input using the parameter 'prompt' 
        to ask a question of the user. 
        
        DO NOT INCLUDE THE '[y/n]:' part in the string. It is added 
        automatically.
        
        DEFAULT:  '[y/n]:'
        
    :PARAMETERS:
        prompt:    The "yes or no" question to be asked of the user.
                   DO NOT INCLUDE THE '[y/n]:' part in the string. It is 
                   added automatically.
                   DEFAULT:  '[y/n]:'
        
        bool:      If True, the return is boolean (True for 'yes', false
                   for 'no'). Otherwise the return is capital "YES" or
                   capital "NO"
                   DEFAULT: True (returns True for "YES" or 
                            False for "NO")
            
        full_yes: If True, the 'yes' response ONLY will require the 
                  full word "yes".
                  DEFAULT: True
                   
                   
        full_no: If True, the 'no' response ONLY will require the 
                   full word "no".
                  DEFAULT: False
                   
        default: If set to "y", hitting the enter key in response to 
                 the prompt registers as "y".
                 
                 If set to "n", hitting the enter key in response to 
                 the prompt registers as "n".
                                  
                 If set to "None" or (blank), a response is required. 
                 
                 DEFAULT: None

                
    :RETURNS:
        Capital "YES" or capital "NO" be default.
        
        If parameter 'bool' is True returns True for "yes" or 
        False for "no".
    
    :EXAMPLE:
        from common.ynprompt import yn
        
        if yn("Do you want to do this?): 
            # do it
        else:
            # Cancelled
    """
    def _return_yes():
        if bool is True: return True
        else:    return "YES"
        
    def _return_no():
        if bool is True: return False
        else:    return "NO"

    default  = str(default).lower()
    
    prompt_yes = "yes" if full_yes else "y"
    prompt_no = "no" if full_no else "n"

    if "y" in default.lower(): # Emphasize yes
        _prompt = ''.join(["\n", str(prompt), "[", prompt_yes.upper(), "/", prompt_no, "]:"])
    elif "n" in default.lower():  # Emphasize no  
        _prompt = ''.join(["\n", str(prompt), "[", prompt_yes, "/", prompt_no.upper(), "]:"])
    else:  # Emphasize neither
        _prompt = ''.join(["\n", str(prompt), "[", prompt_yes, "/", prompt_no, "]:"])
        
    yesno = input(_prompt)
    yesno = yesno.lower()
        
    if "y" in yesno:
        if (full_yes is True) and (not "yes" in yesno):
            print("Please type the full word 'yes' ...")
            return yn(prompt) # Recursive loop
        else:
            return _return_yes()

    elif "n" in yesno:
        if (full_no) and (not "no" in yesno):
            print("Please type the full word 'no' ...")
            return yn(prompt) # Recursive loop
        else:
            return _return_no()
    else:
        if   "y" in default: return _return_yes()
        elif "n" in default and default != "none": return _return_no()
        else:  
            print("Please enter a specific response ...")
            return yn(prompt) # Recursive loop
        
if __name__ == '__main__':
    test = yn("", 
        bool = False, 
        full_yes = False, 
#           full_no = False, 
        default = "no"
          )
    print(test)
        
