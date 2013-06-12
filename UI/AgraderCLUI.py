# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

from CLUI import CLUI
from AgraderBaseUI import AgraderBaseUI
from getpass import getpass

class AgraderCLUI(CLUI, AgraderBaseUI):
##### NOTIFICATIONS ######
    def __init__(self, args):
        super(AgraderCLUI, self).__init__(args)
    
    def RawOutput(self, msg):
        print msg

    def notify(self, msg):
        if self.isInteractive():
            self.RawOutput(msg)
    
    def notifyError(self, msg):
        self.notify(msg)
        if self.promptBool('Exit program? '):
            exit()

    def notifyProblemSetup(self, assignment):
        #TODO: print in 2nd line
        self.notify('############################################################')
        self.notify('$$$$$$$$$$$$$$$$$$     PROBLEM      $$$$$$$$$$$$$$$$$$$$$$$$\n')

        try:
            self.notify(assignment.name)
        except AttributeError:
            self.notify("Next Problem")
        
        self.notify('\n\n')
        
    def notifyProblemCleanup(self, assignment):
        #self.notify('\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        self.notify('###########################################################\n\n')
    
    def notifySubmissionSetup(self, submission):
        self.notify('############################################################')
        self.notify('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        self.notify('$$$$$$$$$$$$$$$$$     SUBMISSION      $$$$$$$$$$$$$$$$$$$$$$\n')
        
        try:
            self.notify('By %s' % submission.name)
        except AttributeError:
            self.notify('By unknown submitter.')
        self.notify('') #newline

    def notifySubmissionCleanup(self, submission):
        self.notify('$$$$$$$$$$$$$$$     END SUBMISSION      $$$$$$$$$$$$$$$$$$$$')
        self.notify('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        self.notify('############################################################\n\n\n')
