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
sys.path.append('~/repos/AGrader') #directory where I store the Agrader source code
from Assignment import Assignment
from cs143b_callbacks import *

# get workspace
from Workspace import Workspace
workspace = Workspace.GetWorkspace()

class MyAssignment(Assignment):
    
    def __init__(self, submission, args):
        super(MyAssignment, self).__init__()

        # skip if already graded
        if submission.endswith('.graded'):
            continue

        self.submission_deadline = time.strptime('Mon Apr 22 23:59:59 2013 PDT')
        
        self.temp_filename = os.path.join(args.assignment_dir, '.temp_output_file')
        self.args = args
        self.submission = submission

        username = os.path.split(submission)[-1].strip().lower()
        self.grade_key = username
        self.name = username

        self.grades = workspace.getGrades(self.grade_key)
        self.gradebook = workspace.gradebook
        self.ui = workspace.ui

        # Callbacks
        self.addCallback('setup', SubmissionSetup)
        self.addCallback('cleanup', SubmissionCleanup)
        #self.addCallback('grade', SubmitGrades)

def SubmissionGenerator(args):
    temp_filename = os.path.join(args.assignment_dir, '.temp_output_file')

    for username in sorted(listdir(join(args.assignment_dir, 'submissions'))):
        submission = join(args.assignment_dir, 'submissions', username)
        # If we specified a specific set of submissions, only execute for them
        if (not args.regrade and '.graded' in listdir(submission)) or (args.submissions and username not in args.submissions):
            continue

        sub = MyAssignment(submission, args)
        yield sub

    #finalCleanup
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
