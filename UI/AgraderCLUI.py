# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

from CLUI import CLUI
from AgraderBaseUI import AgraderBaseUI
from getpass import getpass

CRLF = '\r\n'

class AgraderCLUI(CLUI, AgraderBaseUI):
##### NOTIFICATIONS ######
    def __init__(self, args):
        super(AgraderCLUI, self).__init__(args)
    
    def RawOutput(self, msg):
        print msg

    def notify(self, msg):
        print msg
    
    def notifyError(self, msg):
        self.notify(msg)
        if self.promptBool('Exit program? '):
            exit()

    def notifyProblemSetup(self, assignment):
        #TODO: print in 2nd line
        print '############################################################'
        print '$$$$$$$$$$$$$$$$$$     PROBLEM      $$$$$$$$$$$$$$$$$$$$$$$$\n'

        try:
            print assignment.name
        except AttributeError:
            print "Next Problem"
        
        print '\n\n'    
        
    def notifyProblemCleanup(self, assignment):
        #print '\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
        print '###########################################################\n\n'
    
    def notifySubmissionSetup(self, submission):
        print '############################################################'
        print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        print '$$$$$$$$$$$$$$$$$     SUBMISSION      $$$$$$$$$$$$$$$$$$$$$$\n'
        
        try:
            print 'By %s' % submission.name
        except AttributeError:
            print 'By unknown submitter.'
        print
    
    def notifySubmissionCleanup(self, submission):
        print '$$$$$$$$$$$$$$$     END SUBMISSION      $$$$$$$$$$$$$$$$$$$$'
        print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        print '############################################################\n\n\n'
