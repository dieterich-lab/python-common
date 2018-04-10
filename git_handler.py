#!/usr/bin/env python3
"""
Inception  - 2018-03-05 : Martin Reifferscheid
2018-03-05 -            : Mike Rightmire

https://github.com/joshfire/jsonform/wiki
"""
__author__      = "Mike Rightmire"
__copyright__   = "University Heidleberg DieterichLab"
__license__     = "Not licensed for private use."
__version__     = "0.9.0.0"
__maintainer__  = "Mike Rightmire"
__email__       = "Michael.Rightmire@BiocomSoftware.Com"
__status__      = "Development"

from git import Repo
from git import Git
from inspect import stack

import datetime
import os

class GitHandler():
    def __init__(self):
        pass

    @classmethod         
    def git_push(self, repo, idfile, feedback_title  = "Success!", feedback_string = ""): 
        """
        :NAME:
        
        :DESCRIPTION:
            repo    :(str) FULL PATH to the local repository (on the drive). 
            
            idfile  :(str) FULL PATH to the ssh identity file (private key for 
                           git)
            
            feedback_title:(str) Feedback title contains output data for the 
                                 title of the web page. Defaults to "Success!". 
                                 Is returned so can be changed during 
                                 processing.
            
            feedback_string:(str) Feedback string contains output data for the 
                                  body of the web page. Defaults to "". 
                                  Is returned so can be changed during 
                                  processing.
        
        :RETURNS:
            feedback_title, feedback_string, log_message
        """           
        # Set parameters. 
        # GIT will be using ssh with a key. This all has to be set up on the server.
        response = ""
        git_ssh_cmd = 'ssh -i {}'.format(idfile)
        print("git_ssh_cmd = '{}'".format(git_ssh_cmd))
        response += "\ngit_ssh_cmd = '{}'".format(git_ssh_cmd)
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = ''.join([now, ":", "Automatically updated by metadata.input_handler."])
        # Do the actual update
        try:
            repo = Repo(repo)
            print("Setting repo ='{}'".format(str(repo)))
            response += "\nSetting repo ='{}'".format(str(repo))
    
            print("Running 'add .'")
            response += "\nRunning 'add .'"        
            repo.git.add(".")
            
            print("Running 'commit -m {}'".format(msg))
            response += "\nRunning 'commit -m {}'".format(msg)        
            repo.git.commit("-m {}".format(msg))
    
            with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                print("Running 'push'")
                response += "\nRunning 'push'..."        
                result = repo.git.push()            
                print(str(result))
                response += result
    
            feedback_string = ''.join([feedback_string, "<br>", "GIT UPDATE: OK (OUTPUT: {})".format(str(result))])
        
        except Exception as e:
            if "nothing to commit" in str(e):
                feedback_string = ''.join([feedback_string, "<br>", "GIT UPDATE: OK (Nothing to commit)"])
            else:
                err = "GIT update failed (ERROR:{})".format(str(e))
                print(err)
                response += ("\n" + err)
                feedback_title  = "There were errors..."
                feedback_string = ''.join([feedback_string, "<br>", err])
        
        return feedback_title, feedback_string, response 

    @classmethod         
    def git_pull(self, repo, idfile, feedback_title  = "Success!", feedback_string = ""): 
        """
        :NAME:
        
        :DESCRIPTION:
            repo    :(str) FULL PATH to the local repository (on the drive). 
            
            idfile  :(str) FULL PATH to the ssh identity file (private key for 
                           git)
            
            feedback_title:(str) Feedback title contains output data for the 
                                 title of the web page. Defaults to "Success!". 
                                 Is returned so can be changed during 
                                 processing.
            
            feedback_string:(str) Feedback string contains output data for the 
                                  body of the web page. Defaults to "". 
                                  Is returned so can be changed during 
                                  processing.
        
        :RETURNS:
            feedback_title, feedback_string, log_message
        """           
        # Set parameters. 
        # GIT will be using ssh with a key. This all has to be set up on the server.
        response = ""
        git_ssh_cmd = 'ssh -i {}'.format(idfile)
        print("git_ssh_cmd = '{}'".format(git_ssh_cmd))
        response += "\ngit_ssh_cmd = '{}'".format(git_ssh_cmd)
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = ''.join([now, ":", "Automatically syncing git repo to local..."])
        # Do the actual update
        try:
            repo = Repo(repo)
            print("Setting repo ='{}'".format(str(repo)))
            response += "\nSetting repo ='{}'".format(str(repo))
    
            with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                print("Running 'pull'")
                response += "\nRunning 'pull'..."        
                result = repo.git.pull()            
                print(str(result))
                response += result
    
            feedback_string = ''.join([feedback_string, "<br>", "GIT UPDATE: OK (OUTPUT: {})".format(str(result))])
        
        except Exception as e:
            err = "GIT update failed (ERROR:{})".format(str(e))
            print(err)
            response += ("\n" + err)
            feedback_title  = "There were errors..."
            feedback_string = ''.join([feedback_string, "<br>", err])
        
        return feedback_title, feedback_string, response 
