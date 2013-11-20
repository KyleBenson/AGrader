# ICS 51 Fall 2013 Lab 2 agrader config file

from os import listdir, system, getcwd, chdir, getcwd, walk, remove
from os.path import isdir, join, split, exists, getmtime
from copy import deepcopy, copy
import os.path
import sys
import time
from datetime import timedelta

# SET USER INTERFACES
# choose which user interface and gradebook connector you want to use
# make sure to use the 'as' keyword so Agrader can reference it properly
sys.path.append('~/repos/AGrader')
#from AGrader.Assignment import Assignment
#from AGrader.Workspace import Workspace
from Assignment import Assignment
from Workspace import Workspace

class MyAssignment(Assignment):
    
    def __init__(self, submission, args):
        super(MyAssignment, self).__init__()

        # get workspace from package
        workspace = Workspace.GetWorkspace()

        self.submission_deadline = time.strptime('Tue Nov 20 11:55:00 2013')
        self.grace_period = timedelta(hours=4)

        self.args = args
        self.submission = submission
        self.expected_output_filename = 'expected_output.txt'
        #self.expected_output_filename = 'expected_output_with_error.txt' # there was a bug in input so this ignored it
        #self.expected_output_filename = 'expected_output_groups.txt'

        username = os.path.split(submission)[-1].strip().lower()
        self.grade_key = username
        self.name = username

        self.gradebook = workspace.gradebook
        self.ui = workspace.ui

        #experiment: instead of getting the grades from gradebook at start, wait until end!
        #doesn't work since getGrades builds the index
        #self.grades = {}
        #TODO: fix that...
        if self.gradebook:
            self.grades = self.gradebook.getGrades(self.grade_key)
        else:
            self.grades = {}

        # if returned grades are None, this submission isn't present in the roster
        if self.grades is None:
            self.ui.notify("Student %s not found in roster, skipping!" % username)
            return

        # Callbacks
        # import example callbacks for this class
        from AGrader.examples.ics51 import ics51_callbacks

        self.addCallback('setup', ics51_callbacks.SubmissionSetup)
        #self.addCallback('grade', ics51_callbacks.GradeMultiTestOutputOutput) #process simulator project
        self.addCallback('grade', ics51_callbacks.CompileCommand)
        self.addCallback('grade', ics51_callbacks.RunCommand)
        self.addCallback('grade', ics51_callbacks.ViewSource)
        self.addCallback('grade', ics51_callbacks.CompareFilesByLine)
        self.addCallback('cleanup', ics51_callbacks.SubmissionCleanup)

def SubmissionGenerator(args):
    '''
    Yields the file name of each output submission file if it wasn't already graded.
    '''
    temp_filename = os.path.join(args.assignment_dir, '.temp_output_file')
    submission_dir = join(args.assignment_dir, 'submissions')

    for username in sorted(listdir(submission_dir)):
        submission = join(args.assignment_dir, 'submissions', username)
        # skip if already graded, unless we are regrading
        if submission.endswith('.graded'):
            # if we are regrading, put the file back in its ungraded state
            if args.regrade:
                new_submission_name = submission.replace('.graded','')
                os.rename(submission, new_submission_name)
                submission = new_submission_name
                username = username.replace('.graded','')
            else:
                continue

        # If we specified a specific set of submissions, only execute for them,
        if (args.submissions and username not in args.submissions):
            continue

        sub = MyAssignment(submission, args)
        sub.temp_filename = temp_filename
        sub.submission_dir = submission_dir
        yield sub

    #finalCleanup
    if os.path.exists(temp_filename):
        os.remove(temp_filename)


######################################################################
####################  TEST MAIN  #####################################
######################################################################

def TestGenerator():
    args = lambda:0
    args.assignment_dir = os.getcwd()
    args.submissions = None
    for sub in SubmissionGenerator(args):
        print sub.name

test_submission = 'tcathers'
def TestParseOutput():
    from AGrader.examples.ics51 import ics51_callbacks
    from AGrader.examples.ics51 import ics51_callbacks
    tests = ics51_callbacks.ParseOutput('expected_output.txt')
    tests = ics51_callbacks.ParseOutput('expected_output.txt')
    print 'expected output:'
    print 'total of %d tests:\n%s' % (len(tests), tests)
    print

    tests2 = ics51_callbacks.ParseOutput('submissions/' + test_submission)
    tests2 = ics51_callbacks.ParseOutput('submissions/' + test_submission)
    print 'actual output:'
    print 'total of %d tests:\n%s' % (len(tests2), tests2)
    print
    print 'are they equal? %d' % (tests == tests2)

def TestGradeOutput():
    #create blank object
    from AGrader.examples.ics51 import ics51_callbacks
    from AGrader.examples.ics51 import ics51_callbacks
    assignment = lambda:0
    assignment.filename = 'submissions/tcathers'
    assignment.expected_output_filename = 'expected_output.txt'
    assignment.grades = {}
    assignment.ui = AGrader.Workspace.Workspace.GetWorkspace().ui

    ics51_callbacks.GradeOutput(assignment)
    ics51_callbacks.GradeOutput(assignment)

def Test():
    TestGenerator()
    TestParseOutput()
    TestGradeOutput()

if __name__ == '__main__':
    print 'Testing...'
    Test()
