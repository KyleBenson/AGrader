# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

class BaseUI:
####### PROMPTS ########
      def __init__(self, args):
            pass

      def __PromptType(self, value_type, msg, err_msg='Please enter a valid value.'):
            pass

      def PromptBool(self, msg=None):
            pass

      def PromptStr(self, msg=None):
            pass

      def PromptInt(self, msg=None):
            pass

      def PromptFloat(self, msg=None):
            pass

      def PromptIndex(self, options, msg=None):
            pass

      def PromptPassword(self, msg=None):
            pass

      def PromptContinue(self, msg=None):
            pass

      ##### NOTIFICATIONS ######
      def Notify(self, msg):
            pass

      def NotifyError(self, msg):
            pass
      
      def NotifySubmissionSetup(self, submission):
            pass

      def NotifyProblemSetup(self, problem):
            pass

      def NotifySubmissionTearDown(self, submission):
            pass

      def NotifyProblemTearDown(self, problem):
            pass
