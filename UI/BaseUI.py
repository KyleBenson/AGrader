# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

class BaseUI:
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
            pass

      ##### NOTIFICATIONS ######
      def Notify(self, msg):
            pass

      def NotifyError(self, msg, show_help=False):
            pass
      
      def NotifySubmissionSetup(self, submission):
            pass

      def NotifyProblemSetup(self, problem):
            pass

      def NotifySubmissionTearDown(self, submission):
            pass

      def NotifyProblemTearDown(self, problem):
            pass
