# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

class BasePromptUI:
####### PROMPTS ########
      def __init__(self, args):
            pass

      def promptType(self, value_type, msg=None, err_msg='Please enter a valid value.'):
            pass

      def promptBool(self, msg=None):
            pass

      def promptStr(self, msg=None):
            pass

      def promptInt(self, msg=None):
            pass

      def promptFloat(self, msg=None):
            pass

      def promptIndex(self, options, msg=None):
            pass

      def promptPassword(self, msg=None):
            pass

      def promptContinue(self, msg=None):
            pass
