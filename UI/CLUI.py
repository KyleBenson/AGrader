# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

from BaseUI import BaseUI
from getpass import getpass

class CLUI(BaseUI):
    
    def __init__(self, args):
        try:
            self.verbose = args.verbose
        except AttributeError:
            self.verbose = False
    
####### PROMPTS ########
    def PromptStr(self, msg=None):
        if not msg:
            msg = 'Please enter a string: '

        return raw_input(msg)

    def __PromptType(self, value_type, msg, err_msg='Please enter a valid value.'):
        result = None
        while result is None:
            try:
                result = value_type(self.PromptStr(msg))
            except ValueError:
                print err_msg
                result = None

        return result

    def PromptBool(self, msg=None):
        err_msg = 'Please enter yes, no, y, n, or press enter to choose yes'
        if not msg:
            msg = err_msg + ': '
        
        def __BoolCheck(value):
            if value not in ('y', 'n', 'yes', 'no', ''):
                raise ValueError
            else:
                return not value.startswith('n')

        return self.__PromptType(__BoolCheck, msg, msg)
    
    def PromptInt(self, msg=None):
        return self.__PromptType(int, msg if msg else 'Please enter an integer: ', 'Please enter a valid integer.')
    
    def PromptFloat(self, msg=None):
        return self.__PromptType(float, msg if msg else 'Please enter a float: ', 'Please enter a valid number.')

    def PromptIndex(self, options, msg=None):
        if not msg:
            msg = 'Please enter the integer index of which of the following options you want:'

        msg += '\n%s: '.join([''] + options) % tuple(range(1, len(options) + 1))
        msg += '\nEnter choice: '

        def __IdxCheck(value, length=len(options)):
            idx = int(value)
            if idx < 1 or idx > length:
                raise ValueError
            else:
                return idx

        return self.__PromptType(__IdxCheck, msg, 'Please enter a valid index.')
    
    def PromptPassword(self, msg=None):
        if not msg:
            msg = 'Enter password: '
        return getpass(msg)

    def PromptContinue(self, msg=None):
        if not msg:
            msg = 'Press enter to continue...'

        raw_input(msg)

##### NOTIFICATIONS ######
    

    def Notify(self, msg):
        print msg
    
    def NotifyError(self, msg):
        self.Notify(msg)
        if self.PromptBool('Exit program? '):
            exit()

    def NotifyProblemSetup(self, assignment):
        print '############################################################'
        print '$$$$$$$$$$$$$$$$$$     PROBLEM      $$$$$$$$$$$$$$$$$$$$$$$$\n'

        try:
            print assignment.name
        except AttributeError:
            print "Next Problem"
        
        print '\n\n'    
        
    def NotifyProblemTearDown(self, assignment):
        print '\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
        print '###########################################################\n\n'
    
    def NotifySubmissionSetup(self, submission):
        pass
    
    def NotifySubmissionTearDown(self, submission):
        pass

def Test():
    ui = CLUI(None)

    value = ui.PromptBool()
    print 'Read the value:', value
    value = ui.PromptPassword()
    print 'Read the password:', value
    value = ui.PromptIndex(['one', 'two', 'three', 'four'])
    print 'Read the value:', value
    value = ui.PromptFloat()
    print 'Read the value:', value
    value = ui.PromptInt()
    print 'Read the value:', value
    value = ui.PromptContinue()

if __name__ == '__main__':
    Test()
