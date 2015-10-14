# Abstract base class user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

class BasePromptUI(object):
      '''
      Defines some primitive, yet extensible and flexible, type prompts.
      The basis is using a specified value type to contruct the type given the return value from some other prompt (strings being the lowest building block).
      Implement promptStr and promptPassword to bring this class to life.
      '''

      def __init__(self, args):
            self.newline = '\r\n'

            try:
                  self._interactive = args.interactive
            except AttributeError:
                  self._interactive = True

            try:
                  self.verbose = args.verbose
            except AttributeError:
                  self.verbose = False

####### SETTINGS #######
      def isInteractive(self):
            return self._interactive

      def setInteractive(self, new_interactive):
            self._interactive = new_interactive

####### BASE PROMPTS ########
      def promptStr(self, msg=None, default=None):
            raise NotImplementedError

      def promptPassword(self, msg=None):
            raise NotImplementedError

####### EXTENDED PROMPTS ########

      def promptType(self, value_type, msg=None, err_msg='Please enter a valid value.', default=None):
            '''Repeatedly prompt the user for input, trying to make the input into a an object of value_type'''
            result = None
            while result is None:
                  try:
                        userInput = self.promptStr(msg, default=default)
                        if userInput == '' and default is not None:
                              return default
                        result = value_type(userInput)
                  except ValueError:
                        print err_msg
                        result = None

            return result

      def promptInt(self, msg=None, default=None):
            if msg is None:
                  msg = 'Please enter an integer%s:' % ((' (default is %i)' % default) if default is not None else '')
            return self.promptType(int, msg, 'Not a valid integer.', default=default)

      def promptFloat(self, msg=None, default=None):
            return self.promptType(float, msg if msg is not None else 'Please enter a float: ',
                                   'Please enter a valid number.', default=default)

      def promptOptions(self, options, msg=None, err_msg=None, default=None):
            if msg is None:
                  msg = 'Please enter one of: %s%s' % (', '.join(options), self.newline)

            def __optionsCheck(value):
                  try:
                        if value not in options:
                              raise ValueError
                        else:
                              return value
                  except TypeError:
                        raise ValueError

            return self.promptType(__optionsCheck, msg, 'Entry not found.' if err_msg is None else err_msg,
                                   default=default)

      def promptIndex(self, options, msg=None, sep=None):
            if sep is None:
                  sep = (self.newline + '  %s: ')

            if msg is None:
                  msg = ''.join(['Please enter the integer index of which of the following options you want:', self.newline,
                                 sep.join([''] + options) % tuple(range(1, len(options) + 1)),
                                 self.newline, 'Enter choice: '])

            def __IdxCheck(value, length=len(options)):
                  idx = int(value)
                  if idx < 1 or idx > length:
                        raise ValueError
                  else:
                        return idx

            return self.promptType(__IdxCheck, msg, 'Please enter a valid index.')

      def promptBool(self, msg=None, default=None):
            if not msg:
                  msg = 'Please enter yes, no, y, n, or press enter to choose %s: ' % 'yes' if default else 'no'

            # Change default from a boolean value to the corresponding str
            if default is not None:
                  default = ('y' if default else 'n')

            value = self.promptOptions(('y', 'n', 'yes', 'no', ''), msg, default=default)

            return not value.startswith('n')

      def promptContinue(self, msg=None):
            return self.promptStr(msg if msg is not None else 'Press enter to continue...')

    #TODO:
      '''
      def promptObject(self, prompts, mutator_functions):
      '''
