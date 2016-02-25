import os.path, signal, shutil, sys, time, re, string
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
            command = instance.ui.promptOptions(options, default=options[0])

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
        option = self.ui.promptOptions(sorted(grades.keys()), "Which grades would you like to correct? Leave blank when done.\n", default='')
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
    found_source = False #make sure they submitted anything!
    for (dirpath, dirnames, filenames) in os.walk(self.source_dir):
        #this comprehension 'zips' up the filenames and the time they were submitted (last modified?)
        for f,t in [(os.path.join(dirpath,f),time.localtime(os.path.getmtime(os.path.join(dirpath,f)))) for f in filenames if not dirpath.endswith('removed')]:
            found_source = True
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

    if not found_source:
        # let grader specify grade anyway if they found the source somewhere unexpected
        found_source = not self.ui.promptBool("NO source code found! Is this correct? ", default=True)
        if not found_source:
            penalty = self.possible_points['source_code']
        else:
            penalty = self.ui.promptFloat("Did they lose any points for source code? ", default=0)
    elif found_source:
        penalty = self.ui.promptFloat("Did they lose any points for source code? ", default=0)
    self.grades['sourcecode'] = self.possible_points['source_code'] - penalty

def ParseOutput(fname):
    # to find  the boundary between tests, look for a newline
    with open(fname) as f:
        # start by removing blank lines
        file_lines = [line for line in f.readlines() if len(line) > 1]
        # then change init and error to single-character codes and trim some
        # other garbage while at it
        file_lines = [line.lower().replace('\t','').strip().replace('init', '1').replace('error', '~') for line in file_lines]
        # now turn each line into a string of cases (no spaces)
        file_lines = [line.replace(' ', '') for line in file_lines]

        # trim leading init since example didn't have it
        if file_lines[0].startswith('1'):
            file_lines[0] = file_lines[0][1:]

    return file_lines

def PrintListDifference(self, expected, actual, max_len=20):
    '''
    Prints the difference between two lists of strings.  max_len argument (default = 20) determines space between first and second lists.
    Returns a number representing how different they are (currently the # chars that differ).
    !!max_len currently unimplemented!!
    '''
    self.ui.notify("Expected vv but got vv")

    total_checked = total_wrong = 0

    # Check for early crashes, exits, etc. and penalize for them by
    # subtracting points for all tests beyond the last line present
    # (the chars in that line missed will be accounted for later)
    lines_missing = len(expected) - len(actual)
    if lines_missing > 0:
        total_wrong += len(''.join(expected[len(actual):]))
        self.ui.notify("Last %d lines missing, lost %d points" % (lines_missing, total_wrong))

    for exp, act in zip(expected, actual):
        # check if they didn't finish a test case
        if len(act) < len(exp):
            this_wrong = len(exp) - len(act)
            total_wrong += this_wrong
            self.grades['comments'] += "test %d missed last %d outputs; " % (total_checked, this_wrong)

        line_wrong = False

        # actually check each character
        for expChar, actChar in zip(exp, act):
            if expChar != actChar:
                if expChar == '1':
                    expChar = 'init'
                if expChar == '~':
                    expChar = 'error'
                if actChar == '1':
                    actChar = 'init'
                if actChar == '~':
                    actChar = 'error'
                total_wrong += 1
                line_wrong = True

        if line_wrong:
            self.grades['comments'] += "test %d exp %s, got %s; " % (total_checked, exp, act)
            self.ui.notify('line %d wrong: %s %s' % (total_checked, exp, act))
        total_checked += 1

    return total_wrong

def GradeMultiTestOutput(self):
    '''
    Here we just compare the output of two different programs, one is expected to be completely correct.
    We first parse each file into the individual tests since they are all in one file and each test is worth the same amount.
    Then compare each test one by one, prompting grader if they differ.
    '''
    #parse tests into nested lists
    tests = ParseOutput(self.submission)
    expected_tests = ParseOutput(self.expected_output_filename)

    total_score = self.possible_points['output']

    total_score -= PrintListDifference(self, expected_tests, tests)

    return total_score


def GradeProcessSimulatorProjectOutput(self):
    '''
    Wraps the implementation of grading the output so we can choose to mark
    a submission as not automatically gradeable.
    '''

    total_score = GradeMultiTestOutput(self)
    if total_score != self.possible_points['output']:
        if self.ui.promptBool("Scored a %d. Mark this submission as ungradeable? " % total_score, default=False):
            self.grades['manualgradingneeded'] = 'X'
        else:
            self.grades['output'] = total_score

    else:
        self.grades['output'] = total_score
        self.ui.promptContinue("Output graded. Total score(%d possible): %d" % (self.possible_points['output'], total_score))


def FilesystemProjectMassageOutput(fname):
    '''
    Modify the output in the given file to make it match the expected output.
    Lower-case everything, remove commas, etc.
    '''
    massaged_lines = []

    with open(fname) as f:
        file_lines = f.readlines()

        # trim leading newlines
        while file_lines[0] == '\n':
            file_lines = file_lines[1:]

        # now massage the lines and remove any empty lines
        for line in file_lines:
            # skip newlines
            if line == '\n':
                continue

            else:
                # so many binary characters, here we strip non-printable ones with a recipe taken from
                # http://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python
                # ignores unicode, apparently, too
                line = ''.join(filter(lambda x: x in string.printable, line))

                line = line.strip().replace('\t','').replace('\n','').lower().replace('.','').replace(',','')#.replace(' ', '')

            # lines not given very explicit output formats should be shortened
            # do this after massaging in case of character case differences
            if 'error' in line:
                line = 'error'

            # some people always said restored, never intialized
            line = line.replace('restored', 'initialized')

            # some people say '1 bytes read'
            line = line.replace('byte read', 'bytes read')

            # some people say 'file abc 23, file foo 64', so I just
            line = line.replace('file', '')

            # some people do 'index = 1'
            line = line.replace(' = ', '=')

            # some people do 'bytes read:10'
            line = line.replace(': ', ':')

            # typo...
            line = line.replace('intialized', 'initialized')

            # someone said this...
            line = line.replace('disk initiated', 'disk initialized')
            line = line.replace('deleted', 'destroyed')

            massaged_lines.append(line)

    return massaged_lines


def GradeFilesystemProjectOutput(self):
    '''
    Here we just compare the output of two different programs, one is expected to be completely correct.
    We first parse each file into lines, massaged to match the expected output.
    Then compare each line, prompting grader if they differ.
    '''
    tests = FilesystemProjectMassageOutput(self.submission)
    expected_tests = FilesystemProjectMassageOutput(self.expected_output_filename)

    #configure score for each line to be equal
    score_per_test = self.possible_points['output']/float(len(expected_tests))

    points_off = score_per_test * PrintListDifference(self, expected_tests, tests)
    default_points = self.possible_points['output'] - points_off

    # prompt for possible corrections if they didn't get 100
    do_prompt = default_points != self.possible_points['output']
    if do_prompt:
        total_score = self.ui.promptInt("Outputs did not match. How much credit should they get? (default = %spts, %spts/line) " % (str(default_points), str(score_per_test)), default=default_points)
    else:
        total_score = default_points

    self.grades['output'] = total_score

    #prompt only if not done already
    if not do_prompt:
        self.ui.promptContinue("Output matches! Total score(%d possible): %d" % (self.possible_points['output'], total_score))


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
