# ICS 23 Fall 2012 Program 3 agrader config file

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

        self.submission_deadline = time.strptime('Tue Apr 23 00:00:00 2013')
        self.grace_period = timedelta(hours=4)

        self.args = args
        self.submission = submission
        self.expected_output_filename = 'expected_output.txt'
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

        # store possible points for each part of the assignment here
        self.possible_points = {}
        
        #source code info
        self.possible_points['source_code'] = 2.5
        self.possible_points['output'] = 100
        self.source_dir = os.path.join(args.assignment_dir, 'sources', username)

        # Callbacks
        # import example callbacks for this class
        from AGrader.examples.cs143b import cs143b_callbacks

        self.addCallback('setup', cs143b_callbacks.SubmissionSetup)
        self.addCallback('grade', cs143b_callbacks.GradeOutput)
        self.addCallback('grade', cs143b_callbacks.ViewSource)
        self.addCallback('cleanup', cs143b_callbacks.SubmissionCleanup)

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
    from AGrader.examples.cs143b import cs143b_callbacks
    tests = cs143b_callbacks.ParseOutput('expected_output.txt')
    print 'expected output:'
    print 'total of %d tests:\n%s' % (len(tests), tests)
    print

    tests2 = cs143b_callbacks.ParseOutput('submissions/' + test_submission)
    print 'actual output:'
    print 'total of %d tests:\n%s' % (len(tests2), tests2)
    print
    print 'are they equal? %d' % (tests == tests2)

def TestGradeOutput():
    #create blank object
    from AGrader.examples.cs143b import cs143b_callbacks
    assignment = lambda:0
    assignment.filename = 'submissions/tcathers'
    assignment.expected_output_filename = 'expected_output.txt'
    assignment.grades = {}
    assignment.ui = AGrader.Workspace.Workspace.GetWorkspace().ui

    cs143b_callbacks.GradeOutput(assignment)

def Test():
    TestGenerator()
    TestParseOutput()
    TestGradeOutput()

if __name__ == '__main__':
    print 'Testing...'
    Test()
