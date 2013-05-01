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
sys.path.append('~/repos/Agrader') #directory where I store the Agrader source code
from Assignment import Assignment
from ics23_callbacks import *

# get workspace
from Workspace import Workspace
workspace = Workspace.GetWorkspace()

# for Java classpaths
classpath_sep = ':'

class ICS23Program3(Assignment):
    
    def __init__(self, submission_dir, args):
        super(ICS23Program3, self).__init__()

        self.two_extra_credit_deadline = time.strptime('Thu Dec 6 23:59:59 2012')
        self.three_extra_credit_deadline = time.strptime('Wed Dec 5 23:59:59 2012')
        self.submission_deadline = time.strptime('Fri Dec 7 23:59:59 2012')
        self.package = 'edu.uci.ics.pattis.ics23.collections.'
        
        self.expected_big_oh = {'a' : '''//put           : O(1)
//putAll        : O(M)
//remove        : O(1)
//clear         : O(1)
//get           : O(1)
//containsKey   : O(1)
//containsValue : O(N)
//entries       : O(1) 
//keys          : O(1)
//values        : O(1)
//  hasNext     : O(1)
//  next        : O(1)
//  remove      : O(1)
//isEmpty       : O(1)
//size          : O(1)
//toArray       : O(N)
//newEmpty      : O(1)
//shallowCopy   : O(N)
//toString      : O(N)'''.replace(' ', '').lower().split('\n')}
#//retainAll   : O(N Log N)*O(contains(M))

        self.temp_filename = os.path.join(args.assignment_dir, '.temp_output_file')
        self.args = args
        self.project_dir = args.assignment_dir
        self.package_dir = os.path.join(self.project_dir, 'edu/uci/ics/pattis/ics23/collections/')

        self.classpath = classpath_sep.join([os.path.join(self.project_dir, f) for f in ['deps/introlib.jar',
                                                                                         'deps/collections.jar',
                                                                                         'deps/junit-4.7.jar',
                                                                                         'edu/uci/ics/pattis/ics23/collections/',
                                                                                         '' #includes project_dir
                                                                                         ]])
        self.submission_dir = submission_dir

        username = os.path.split(submission_dir)[-1].strip().lower()
        self.grade_key = username
        self.name = username

        # Creates problems and we share some local info with them
        problemFactory = deepcopy(self)
        problemFactory.compiled_files = './edu/uci/ics/pattis/ics23/collections/*.java'

        # Resources should be shared as references not copies
        self.grades = workspace.getGrades(self.grade_key)
        self.gradebook = workspace.gradebook
        self.ui = workspace.ui
        # Callbacks
        self.addCallback('setup', SubmissionSetup)
        self.addCallback('cleanup', SubmissionCleanup)
        #self.addCallback('grade', SubmitGrades)

        ### Defining which submission files we expect to find
        expected_submissions = ['a','b']

        ### Create each assignment
        for program in sorted(listdir(submission_dir)):
            if program in ['.graded']:
                continue
            try:
                expected_submissions.remove(program)
            except ValueError:
                self.ui.notifyError("Unrecognized program %s" % program)
            dirpath = join(submission_dir, program)
            if not os.path.isdir(dirpath):
                continue
            filenames = listdir(dirpath)

            if not [f.endswith('.java') for f in filenames] or dirpath.endswith('removed') or (not args.regrade and '.graded' in filenames):
                continue

            problem = deepcopy(problemFactory) #keep same state info
            problem.dirpath = dirpath

            problem.name = None
            for fname in filenames:
                if fname != '.graded' and fname.endswith('.java'):
                    if problem.name is None:
                        problem.name = fname.split('.')[0]
                    problem.filename = os.path.join(dirpath, fname)
                    break
            else:
                self.ui.notifyError("No java files found in %s!" % dirpath)

            #build subproblems and add callbacks
            problem.addCallback('setup', self.ui.notifyProblemSetup)
            problem.addCallback('setup', ProgramSetup)

            if program == 'a':
                problem.addCallback('setup', CompileCommand)
                problem.addCallback('setup', RunCommand)
                problem.addCallback('cleanup', ParseFailedTests)
                problem.addCallback('cleanup', RecordWhichFailed)
            else:
                problem.addCallback('cleanup', GradeGraph)
            problem.addCallback('cleanup', self.ui.notifyProblemCleanup)

            if program == 'a':
                problem.run_file = 'org.junit.runner.JUnitCore ' + self.package + 'TestGraph'
            elif program == 'b':
                problem.run_file = 'Dijkstra'
            else:
                workspace.ui.notifyError('Unrecognized problem %s' % program)

            self.addAssignment(problem)

            # copy needs references not copies (shallow for this part)
            problem.ui = self.ui
            problem.grades = self.grades

        # mark unsubmitted programs with X or total possible wrong
        if expected_submissions:
            for sub in expected_submissions:
                for g in [k for k in self.grades.keys() if k.startswith(sub)]:
                    # bigo requires a 0 in the spreadsheet
                    if 'bigo' in g:
                        self.grades[g] = '0'
                    else:
                        self.grades[g] = 'X'
                        
                        
#end assignment definition


def SubmissionGenerator(args):
    temp_filename = os.path.join(args.assignment_dir, '.temp_output_file')

    for username in sorted(listdir(join(args.assignment_dir, 'submissions'))):
        submission_dir = join(args.assignment_dir, 'submissions', username)
        # If we specified a specific set of submissions, only execute for them
        if (not args.regrade and '.graded' in listdir(submission_dir)) or (args.submissions and username not in args.submissions):
            continue

        sub = ICS23Program3(submission_dir, args)
        yield sub

    #finalCleanup
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
