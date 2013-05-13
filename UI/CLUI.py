# Command-line user interface for AGrader
# @author: Kyle Benson
# (c) Kyle Benson 2012

from BasePromptUI import BasePromptUI
from getpass import getpass

class CLUI(BasePromptUI):
    
    def __init__(self, args):
        super(CLUI, self).__init__(args)

####### PROMPTS ########
    def promptStr(self, msg=None, default=None):
        if self.isInteractive():
            value = raw_input(msg if msg is not None else 'Please enter a string%s: ' % (' (default is %s)' % default) if default is not None else '')
        else:
            return default

        if default is not None and not value:
            value = default
        return value

    def promptPassword(self, msg=None):
        if not msg:
            msg = 'Enter password: '
        return getpass(msg)


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
