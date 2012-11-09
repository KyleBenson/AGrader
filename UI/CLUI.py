# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

import BaseUI
from getpass import getpass

class CLUI(BaseUI):
    
    def __init__(self):
        pass
    
####### PROMPTS ########
    def PromptBool(self, msg, show_help=False):
        
        pass
    
    def PromptInt(self, msg, show_help=False):
        pass
    
    def PromptFloat(self, msg, show_help=False):
        pass
    
    def PromptStr(self, msg, show_help=False):
        pass

    def PromptIndex(self, msg, options, show_help=False):
        pass
    
    def PromptPassword(self, msg=None):
        pass

    def PromptContinue(self, msg=None):
        if not msg:
            msg = 'Press enter to continue...'

        raw_input(msg)

##### NOTIFICATIONS ######
    

    def Notify(self, msg):
        pass
    
    def NotifyError(self, msg, show_help=False):
        pass

    def NotifyProblemSetup(self, assignment):
        print '############################################################'
        print '$$$$$$$$$$$$$$$$$$     PROBLEM      $$$$$$$$$$$$$$$$$$$$$$$$\n'

        try:
            print assignment.name
        except AttributeError:
            print "Next Problem"
        
        print '\n\n'    
        
    def NotifyProblemTearDown(self, assignment):
        print '\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
        print '###########################################################\n\n'
    
    def NotifySubmissionSetup(self, submission):
        pass
    
    def NotifySubmissionTearDown(self, submission):
        pass

    
