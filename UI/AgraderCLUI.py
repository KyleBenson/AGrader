# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

from CLUI import CLUI
from AgraderBaseUI import AgraderBaseUI
from getpass import getpass

CRLF = '\r\n'

class AgraderCLUI(CLUI, AgraderBaseUI):
##### NOTIFICATIONS ######
    
    def RawOutput(self, msg):
        print msg

    def Notify(self, msg):
        print msg
    
    def NotifyError(self, msg):
        self.Notify(msg)
        if self.promptBool('Exit program? '):
            exit()

    def NotifyProblemSetup(self, assignment):
        #TODO: print in 2nd line
        print '############################################################'
        print '$$$$$$$$$$$$$$$$$$     PROBLEM      $$$$$$$$$$$$$$$$$$$$$$$$\n'

        try:
            print assignment.name
        except AttributeError:
            print "Next Problem"
        
        print '\n\n'    
        
    def NotifyProblemCleanup(self, assignment):
        print '\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
        print '###########################################################\n\n'
    
    def NotifySubmissionSetup(self, submission):
        pass
    
    def NotifySubmissionCleanup(self, submission):
        pass
