# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

from BasePromptUI import BasePromptUI

class AgraderBaseUI(BasePromptUI):

      ##### NOTIFICATIONS ######

      def RawOutput(self, msg):
            pass

      def Notify(self, msg):
            pass

      def NotifyError(self, msg):
            pass
      
      def NotifySubmissionSetup(self, submission):
            pass

      def NotifyProblemSetup(self, problem):
            pass

      def NotifySubmissionCleanup(self, submission):
            pass

      def NotifyProblemCleanup(self, problem):
            pass
