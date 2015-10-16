# CS 143A Fall 2015 HW 1 agrader config file

from os import listdir
from os.path import join
import os.path
import datetime

# SET USER INTERFACES
# choose which user interface and gradebook connector you want to use
# make sure to use the 'as' keyword so Agrader can reference it properly
from AGrader.Assignment import Assignment
from callbacks import *

# get workspace
from AGrader.Workspace import Workspace

class MyAssignment(Assignment):

    def __init__(self, submission_dir, args):
        super(MyAssignment, self).__init__()

        # HW1 deadline
        #self.submission_deadline = datetime.datetime.strptime('Wed Oct 7 16:30:00 2015', "%a %b %d %H:%M:%S %Y")
        # HW2 deadline
        self.submission_deadline = datetime.datetime.strptime('Wed Oct 14 16:30:00 2015', "%a %b %d %H:%M:%S %Y")

        self.temp_filename = os.path.join(args.assignment_dir, '.temp_output_file')
        self.args = args
        self.assignment_dir = args.assignment_dir

        self.submission_dir = submission_dir

        username = os.path.split(submission_dir)[-1].strip().lower()
        self.grade_key = username
        self.name = username

        # Resources should be shared as references not copies
        workspace = Workspace.GetWorkspace()
        self.grades = workspace.getGrades(self.grade_key)
        # need to make this an empty string so we can append to it
        self.grades['comments'] = ''
        self.gradebook = workspace.gradebook
        self.ui = workspace.ui

        # Callbacks
        self.addCallback('setup', SubmissionSetup)
        self.addCallback('grade', CheckSubmissionTime)
        self.addCallback('grade', ViewPart1)

        # HW1 Callbacks
        #self.addCallback('grade', GradeAverage)
        #self.addCallback('grade', GradeCompute)

        # HW2 Callbacks
        self.addCallback('grade', GradeHandleSignals)
        self.addCallback('grade', GradeSendSignals)

        self.addCallback('cleanup', SubmissionCleanup)
        #self.addCallback('grade', SubmitGrades)


#end assignment definition


def SubmissionGenerator(args):
    temp_filename = os.path.join(args.assignment_dir, '.temp_output_file')

    for username in sorted(listdir(join(args.assignment_dir, 'submissions'))):
        submission_dir = join(args.assignment_dir, 'submissions', username)
        # If we specified a specific set of submissions, only execute for them
        if (not args.regrade and '.graded' in listdir(submission_dir)) or (args.submissions and username not in args.submissions):
            continue

        sub = MyAssignment(submission_dir, args)
        yield sub

    #finalCleanup
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
