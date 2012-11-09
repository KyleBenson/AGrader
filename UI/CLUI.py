# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

from BasePromptUI import BasePromptUI
from getpass import getpass

CRLF = '\r\n'

class CLUI(BasePromptUI):
    
    def __init__(self, args):
        try:
            self.verbose = args.verbose
        except AttributeError:
            self.verbose = False
    
####### PROMPTS ########
    def promptStr(self, msg=None):
        value = raw_input(msg if msg else 'Please enter a string: ')
        return value

    def promptType(self, value_type, msg=None, err_msg='Please enter a valid value.'):
        '''Repeatedly prompt the user for input, trying to make the input into a an object of value_type'''
        result = None
        while result is None:
            try:
                result = value_type(raw_input(msg))
            except ValueError:
                print err_msg
                result = None

        return result

    def promptInt(self, msg=None):
        return self.promptType(int, 'Please enter an integer:', 'Not a valid integer.')
    
    def promptFloat(self, msg=None):
        return self.promptType(float, msg if msg else 'Please enter a float: ', 'Please enter a valid number.')

    def promptOptions(self, options, msg=None, err_msg=None):
        if msg is None:
            msg = 'Please enter one of: %s%s' % (', '.join(options), CRLF)

        def __optionsCheck(value):
            try:
                if value not in options:
                    raise ValueError
                else:
                    return value
            except TypeError:
                raise ValueError

        return self.promptType(__optionsCheck, msg, 'Entry not found.' if err_msg is None else err_msg)

    def promptIndex(self, options, msg=None, sep=(CRLF + '  %s: ')):
        if msg is None:
            msg = ''.join(['Please enter the integer index of which of the following options you want:', CRLF, 
                           sep.join([''] + options) % tuple(range(1, len(options) + 1)),
                           CRLF, 'Enter choice: '])

        def __IdxCheck(value, length=len(options)):
            idx = int(value)
            if idx < 1 or idx > length:
                raise ValueError
            else:
                return idx

        return self.promptType(__IdxCheck, msg, 'Please enter a valid index.')
    
    def promptBool(self, msg=None, assume_yes=True):
        if not msg:
            msg = 'Please enter yes, no, y, n, or press enter to choose %s: ' % 'yes' if assume_yes else 'no'

        value = self.promptOptions(('y', 'n', 'yes', 'no', ''), msg)
        return not value.startswith('n')
    
    def promptPassword(self, msg=None):
        if not msg:
            msg = 'Enter password: '
        return getpass(msg)

    def promptContinue(self, msg=None):
        return self.promptStr(msg if msg else 'Press enter to continue...')

    #TODO:
    '''
    def promptObject(self, prompts, mutator_functions):
    '''

def Test():
    ui = CLUI(None)

    print 5
    value = ui.promptInt()
    print 'Read the value:', value
    value = ui.promptPassword()
    print 'Read the password:', value
    value = ui.promptIndex(['one', 'two', 'three', 'four'])
    print 'Read the value:', value
    value = ui.promptOptions(['one', 'two', 'three', 'four'])
    print 'Read the value:', value
    value = ui.promptFloat()
    print 'Read the value:', value
    value = ui.promptBool()
    print 'Read the value:', value
    value = ui.promptContinue()

if __name__ == '__main__':
    Test()
