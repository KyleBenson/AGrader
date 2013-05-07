# ICS 23 Fall 2012 Program 3 agrader config file

from os import listdir, system, getcwd, chdir, getcwd, walk, remove
from os.path import isdir, join, split, exists, getmtime
from copy import deepcopy, copy
import os.path
import sys
import time

# SET USER INTERFACES
# choose which user interface and gradebook connector you want to use
# make sure to use the 'as' keyword so Agrader can reference it properly
import AGrader

class MyAssignment(AGrader.Assignment.Assignment):
    
    def __init__(self, submission, args):
        super(MyAssignment, self).__init__()

        # get workspace from package
        workspace = AGrader.Workspace.Workspace.GetWorkspace()

        self.submission_deadline = time.strptime('Tue Apr 23 04:00:00 2013')
        
        self.args = args
        self.submission = submission

        username = os.path.split(submission)[-1].strip().lower()
        self.grade_key = username
        self.name = username

        self.grades = workspace.getGrades(self.grade_key)
        self.gradebook = workspace.gradebook
        self.ui = workspace.ui

        # Callbacks
        # import example callbacks for this class
        from AGrader.examples.cs143b import cs143b_callbacks

        self.addCallback('setup', cs143b_callbacks.SubmissionSetup)
        #self.addCallback('grade', GradeOutput)
        self.addCallback('grade', cs143b_callbacks.ViewSource)
        self.addCallback('cleanup', cs143b_callbacks.SubmissionCleanup)

def SubmissionGenerator(args):
    '''
    Yields the file name of each output submission file if it wasn't already graded.
    '''
    temp_filename = os.path.join(args.assignment_dir, '.temp_output_file')

    for username in sorted(listdir(join(args.assignment_dir, 'submissions'))):
        submission = join(args.assignment_dir, 'submissions', username)
        # skip if already graded, unless we are regrading
        if submission.endswith('.graded') and not args.regrade:
            continue

        # If we specified a specific set of submissions, only execute for them,
        if (args.submissions and username not in args.submissions):
            continue

        sub = MyAssignment(submission, args)
        sub.temp_filename = temp_filename
        yield sub

    #finalCleanup
    if os.path.exists(temp_filename):
        os.remove(temp_filename)


######################################################################
####################  TEST MAIN  #####################################
######################################################################

def Test():
    args = lambda:0
    args.assignment_dir = os.getcwd()
    args.submissions = None
    for sub in SubmissionGenerator(args):
        print sub.name
    #assignment = MyAssignment(submission, args)

if __name__ == '__main__':
    print 'Testing...'
    Test()
