import os.path, signal, shutil, sys, time, re
from datetime import timedelta, datetime

########## Callbacks #########

def SetMainMenuSignal(self):
    instance = self
    def __menu_signal_handler(sig, frame):
        # Rebind SIGINT to kill now
        def __exit_signal_handler(sig, frame):
            self.ui.notify('Goodbye!')
            sys.exit(0)
        signal.signal(signal.SIGINT, __exit_signal_handler)

        options = ['Quit',
                   'View/Edit Source',
                   'Compile',
                   'Run']

        while True:
            command = instance.ui.promptList(options, default=options[0])

            if command == 'Quit':
                exit(0)
            elif command == 'Continue':
                return
            elif command == 'View/Edit Source':
                ViewSource(instance)
            elif command == 'View/Edit Grades':
                CorrectGrades(instance)
            elif command == 'Compile':
                CompileCommand(instance)
            elif command == 'Run':
                RunCommand(instance)
            else:
                instance.ui.notify("Unknown option %s" % command)

        SetMainMenuSignal(instance)

    signal.signal(signal.SIGINT, __menu_signal_handler)

def CorrectGrades(self):
    '''
    Prompts the user to correct the grades.
    '''
    # filter out only the keys for this part
    # we hack on a '1) ' for each option since we request the index for changing them
    grades = {(str(i) + ') ' + k):v for i,(k,v) in enumerate(self.grades.items())}

    while True:
        self.ui.ShowGrades(grades)
        option = self.ui.promptList(sorted(grades.keys()), "Which grades would you like to correct? Leave blank when done.\n", default='')
        print option
        if not option:
            break

        new_grade = self.ui.promptStr("What should it be (blank for None)?", default=None)
        try:
            grades[option] = new_grade
        except: # this should never run if promptOptions is correct
            self.ui.notifyError("Bad option somehow")

    # Save the grades we changed
    for k in grades.keys():
        real_key = k.split(')')[-1][1:]
        self.grades[real_key] = grades[k]

def ViewSource(self, prompt=True):
    # open source files with less (I like to use the syntax highlighting lesspipe add-on)
    # open all of the ones within the directory that looks like:
    # $ASSIGNMENT_ROOT/submissions/ucinetid/
    if self.args.verbose:
        self.ui.notify('Viewing source files in directory: %s' % self.source_dir)

    deadline_penalty = 0
    for (dirpath, dirnames, filenames) in os.walk(self.source_dir):
        #this comprehension 'zips' up the filenames and the time they were submitted (last modified?)
        for f,t in [(os.path.join(dirpath,f),time.localtime(os.path.getmtime(os.path.join(dirpath,f)))) for f in filenames if f.endswith('.java') and not dirpath.endswith('removed')]:
            print '%-60s \t %20s' % (f, time.asctime(t))
            t = datetime.fromtimestamp(time.mktime(t))
            deadline = datetime.fromtimestamp(time.mktime(self.submission_deadline))

            if t > (deadline + self.grace_period):
                #need to convert the time.struct_time objects into datetime ones
                #we add 1 to days_late since it will be 1 day later than the total # of WHOLE days late, i.e. take the ceiling!
                days_late = (t - deadline).days + 1
                this_deadline_penalty = days_late * 5

                #take the max of all penalties
                #only save this if the penalty is more than the previous
                if this_deadline_penalty > deadline_penalty:
                    deadline_penalty = this_deadline_penalty
                self.ui.notify('Assignment turned in %i days past deadline: -%i points!' % (days_late, deadline_penalty))

        for f in filenames:
            os.system("less '%s'" % os.path.join(dirpath, f))

    # record deadline_penalty
    self.grades['deadlinepenalty'] = deadline_penalty

    penalty = self.ui.promptFloat("Did they lose any points for source code? ", default=0)
    self.grades['sourcecode'] = self.possible_points['source_code'] - penalty

def ParseOutput(fname):
    tests = []
    # to find  the boundary between tests, look for 'init is running'
    # but that string could appear in multiple lines at once, possibly with a newline in between
    # so keep a flag that tells us when we're inside a test or when we're at it's boundary
    # note that we start out with no tests present and so the first occurrence of 'init is running' signals the start of the first test boundary
    inside_test = True
    with open(fname) as f:
        # add each line to the current test
        #    after massaging the line (removing newlines, lowercasing everything, etc.)
        file_lines = f.readlines()
        
        # go through once to see if they use 'init'
        uses_inits = False

        for line in file_lines:
            line = line.replace(' ', '').replace('\t','').lower().replace('isrunning','').replace('.','').replace('\n','').replace('process','')
            if 'init' in line:
                uses_inits = True

        for line in file_lines:
            #remove all whitespace and lowercase, as well as periods
            #also remove the phrase 'is running' since the expected tests don't have it
            line = line.replace(' ', '').replace('\t','').lower().replace('isrunning','').replace('.','').replace('\n','').replace('process','')

            #ignore the 'process terminated' message that some people put at the end.  someone misspelled terminated so I truncated it...
            if 'term' in line:
                continue

            # increment the test # when we reach the end of one
            # but only if we were previously inside a test (or at the very beginning) so as to avoid adding extra tests that aren't really there
            # this is the start of a new test
            if 'init' in line and inside_test:
                tests.append([])
                inside_test = False
            # if they didn't use the 'init' output, let's assume they at least gave us a newline...
            elif not uses_inits and line == '' and inside_test:
                tests.append([])
                inside_test = False
            # ignore newlines
            elif not line:
                continue
            # this is a line inside the test
            elif 'init' not in line:
                inside_test = True
            else:
                continue

            # add this line to the last test
            if inside_test:
                if not len(tests):
                    print "No subtest was ever added to list of tests!"
                    tests.append([])
                tests[-1].append(line)

    return tests

def PrintListDifference(self, expected, actual, max_len=20):
    '''
    Prints the difference between two lists.  max_len argument (default = 20) determines space between first and second lists.
    Returns a number representing how different they are (currently the # lines that differ).  
    !!max_len currently unimplemented!!
    '''
    self.ui.notify("Expected vv but got vv")

    total_checked = total_wrong = 0

    for exp, act in zip(expected, actual):
        total_checked += 1

        if exp != act:
            self.ui.notify('wrong: %s %s' % (exp, act))
            total_wrong += 1
            #self.ui.notify(('%-' + str(max_len) + 's %s') % (exp, act))
    
    #check here for lists of unequal length
    longer_list_len = max(len(expected), len(actual))
    if longer_list_len > total_checked:
        longer_list = expected if len(expected) == longer_list_len else actual
        
        #print the remaining lines
        for val in longer_list[total_checked:]:
            self.ui.notify('unexpected value in %s: ' % ('expected' if longer_list is expected else 'actual') + str(val))
            total_wrong += 1
        
    return total_wrong

def GradeOutput(self):
    '''
    Here we just compare the output of two different programs, one is expected to be completely correct.
    We first parse each file into the individual tests since they are all in one file and each test is worth the same amount.
    Then compare each test one by one, prompting grader if they differ.
    '''
    #parse tests into nested lists
    tests = ParseOutput(self.submission)
    expected_tests = ParseOutput(self.expected_output_filename)

    #configure scoring
    total_score = 0
    score_per_test = self.possible_points['output']/len(expected_tests)

    #go through each test that was run one by one
    #they're a pair at a time since one is the expected output and one is the student's submission

    tests_done = 0
    for test, exp_test in zip(tests, expected_tests):
        if test != exp_test:
            # show what was wrong first
            # by default, and for non-interactive grading, we subtract one point for each line wrong, to a minimum of 0
            default_points = max(0, score_per_test - PrintListDifference(self, exp_test, test))
            
            this_grade = self.ui.promptInt("Test %d did not match. How much credit should they get? (default = %spts) " % (tests_done, str(default_points)), default=default_points)
            total_score += this_grade
        else:
            #all good!
            total_score += score_per_test
        tests_done += 1
             
    self.grades['output'] = total_score
    self.ui.promptContinue("Output graded. Total score(%d possible): %d" % (self.possible_points['output'], total_score))


def SubmissionSetup(self):
    self.ui.notifySubmissionSetup(self)

    SetMainMenuSignal(self)
    #setsignal()

def clearFiles(self):
    try:
        os.remove (self.graded_file)
    except:
        pass

def SubmissionCleanup(self):
    '''Executes after running programs and viewing source'''

    if self.args.verbose:
        print self.grades

    if self.gradebook:
        self.gradebook.submitGrades(self.grades, self.grade_key)

    self.ui.notifySubmissionCleanup(self)

    #save that we already graded this one
    if self.ui.promptBool("set file as graded?", default=True):
        name_after_grading = self.submission + '.graded'

        if not os.path.exists(self.submission):
            self.ui.notifyError("Couldn't find file to rename!")

        os.rename(self.submission, name_after_grading)

        if not os.path.exists(name_after_grading):
            self.ui.notifyError("Couldn't find renamed file!")
