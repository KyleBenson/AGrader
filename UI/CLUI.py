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
    def promptStr(self, msg=None,default=None):
        value = raw_input(msg if msg else 'Please enter a string%s: ' % (' (default is %s)' % default) if default is not None else '')
        if default is not None and not value:
            value = default
        return value

    def promptType(self, value_type, msg=None, err_msg='Please enter a valid value.', default=None):
        '''Repeatedly prompt the user for input, trying to make the input into a an object of value_type'''
        result = None
        while result is None:
            try:
                userInput = raw_input(msg)
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
        return self.promptType(float, msg if msg else 'Please enter a float: ',
                               'Please enter a valid number.', default=default)

    def promptOptions(self, options, msg=None, err_msg=None, default=None):
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

        return self.promptType(__optionsCheck, msg, 'Entry not found.' if err_msg is None else err_msg,
                               default=default)

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
    
    def promptBool(self, msg=None, default=None):
        if not msg:
            msg = 'Please enter yes, no, y, n, or press enter to choose %s: ' % 'yes' if default else 'no'

        # Change default from a boolean value to the corresponding str
        if default:
            default = ('y' if default else 'n')

        value = self.promptOptions(('y', 'n', 'yes', 'no', ''), msg, default=default)
        
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
    import sys
    
#    if len(sys.argv) > 1:
 #       magic = argv[1]

    ui = CLUI(None)

    value = ui.promptInt()
    print 'Read the value:', value
    value = ui.promptInt(default=3)
    print 'Read the value:', value

    value = ui.promptPassword()
    print 'Read the password:', value

    value = ui.promptIndex(['one', 'two', 'three', 'four'])
    print 'Read the value:', value

    value = ui.promptOptions(['one', 'two', 'three', 'four'])
    print 'Read the value:', value

    value = ui.promptOptions(['one', 'two', 'three', 'four'], default='never!!')
    print 'Read the value:', value

    value = ui.promptFloat()
    print 'Read the value:', value

    value = ui.promptBool()
    print 'Read the value:', value

    value = ui.promptBool('give a bool value, but false by default', default='n')
    print 'Read the value:', value

    value = ui.promptContinue()

if __name__ == '__main__':
    Test()
