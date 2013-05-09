import os.path, signal, shutil, sys, time, re

########## Callbacks #########

def SetMainMenuSignal(self):
    instance = self
    def __menu_signal_handler(sig, frame):
        # Rebind SIGINT to kill now
        def __exit_signal_handler(sig, frame):
            print 'Goodbye!'
            sys.exit(0)
        signal.signal(signal.SIGINT, __exit_signal_handler)

        options = ['Quit',
                   'View/Edit Source',
                   'Compile',
                   'Run']

        while True:
            command = ''#instance.ui.promptList(options, default=options[0])

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
    # I put an 'a', 'b', etc. appended to the names for the programs they did
    program_dir = os.path.split(os.path.split(self.filename)[0])[-1]

    # filter out only the keys for this part
    # we hack on a '1) ' for each option since we request the index for changing them
    grades = {k:v for k,v in self.grades.items() if k.startswith(program_dir)}
    grades = {(str(i) + ') ' + k):v for i,(k,v) in enumerate(grades.items())}

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
    source_dir = os.path.join(self.args.assignment_dir, 'submissions', self.name)
    for (dirpath, dirnames, filenames) in os.walk(source_dir):
        for f in filenames:
            os.system('less ' + f)
    penalty = self.ui.promptInt("Did they lose any points for source code? ", default=0)
    self.grades['source_code'] = self.source_code_points - penalty

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
        for line in f.readlines():
            #remove all whitespace and lowercase
            #also remove the phrase 'is running' since the expected tests don't have it
            line = line.replace(' ', '').replace('\t','').lower().replace('isrunning','')

            #ignore the 'process terminated' message that some people put at the end.
            if 'terminated' in line:
                continue

            # increment the test # when we reach the end of one
            # but only if we were previously inside a test (or at the very beginning) so as to avoid adding extra tests that aren't really there
            if 'init' in line and inside_test:
                tests.append([])
                inside_test = False
            # ignore newlines
            elif line == '\n':
                continue
            # this is a line inside the test
            elif 'init' not in line:
                inside_test = True

            # add this line to the last test
            if inside_test:
                tests[-1].append(line)

    return tests


def GradeOutput(self):
    '''
    Here we just compare the output of two different programs, one is expected to be completely correct.
    We first parse each file into the individual tests since they are all in one file and each test is worth the same amount.
    Then compare each test one by one, prompting grader if they differ.
    '''
    program_dir = os.path.split(os.path.split(self.filename)[0])[-1]

    #parse tests into nested lists
    tests = ParseOutput(self.filename)
    expected_tests = ParseOutput(self.expected_output_filename)

    #configure scoring
    total_score = 0
    score_per_test = 100/len(expected_tests)

    #go through each test that was run one by one
    #they're a pair at a time since one is the expected output and one is the student's submission
    for test, exp_test in zip(tests, expected_tests):
        if test != exp_test:
            # show what was wrong first
            self.ui.notify("Expected %s but got %s" % (exp_test, test))

            this_grade = self.ui.promptInt("Tests did not match. How much credit should they get? (default = full points = %dpts) " % score_per_test)
            total_score += this_grade
        else:
            #all good!
            total_score += score_per_test
             
    self.grades['output'] = total_score
    self.ui.promptContinue("Total score: %d" % total_score)


def SubmissionSetup(self):
    self.ui.notifySubmissionSetup(self)

    SetMainMenuSignal(self)
    #setsignal()

    # Check for submission deadlines and penalty for late work
    deadline_penalty = 0
    for (dirpath, dirnames, filenames) in os.walk(self.args.submission_dir):
        #this comprehension 'zips' up the filenames and the time they were submitted (last modified?)
        for f,t in [(os.path.join(dirpath,f),time.localtime(os.path.getmtime(os.path.join(dirpath,f)))) for f in filenames if f.endswith('.java') and not dirpath.endswith('removed')]:
            print '%-60s \t %20s' % (f, time.asctime(t))

            if t > self.submission_deadline:
                days_late = t - self.submission_deadline.days
                deadline_penalty = days_late * 5
                self.ui.notify('Assignment turned in %i days past deadline: -%i points!' % (days_late, deadline_penalty))
                
                break
    # record deadline_penalty
    self.grades['deadline_penalty'] = deadline_penalty

def clearFiles(self):
    try:
        os.remove (self.graded_file)
    except:
        pass

def SubmissionCleanup(self):
    '''Executes after running programs and viewing source'''

    if self.args.verbose:
        print self.grades
    self.gradebook.submitGrades(self.grades, self.grade_key)

    self.ui.notifySubmissionCleanup(self)

    #save that we already graded this one
    if self.ui.promptBool("set file as graded?", default=False):
        os.rename(self.submission, os.path.join(self.submission, '.graded'))
