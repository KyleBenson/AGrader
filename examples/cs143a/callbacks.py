import os.path, signal, shutil, sys, time, re, datetime

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

def FixSource(self):
    os.system('em ' + ' '.join([self.graded_file,
                                self.run_file]))

def CheckSubmissionTime(self):

    for (dirpath, dirnames, filenames) in os.walk(self.submission_dir):
        # skip over compiled files
        t = [datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(dirpath,f))) for f in filenames if f not in ('average', 'compute', self.temp_filename)]
        submission_time = max(t)
        # we (may) need to remove tzinfo as the deadline has no such info
        #submission_time = submission_time.replace(tzinfo=None)

        if submission_time < (self.submission_deadline - datetime.timedelta(days=1)):
            self.ui.notify("early submission!")
            self.grades['percentage'] = 110
        elif submission_time > self.submission_deadline and submission_time < (self.submission_deadline + datetime.timedelta(days=1)):
            self.ui.notify("Assignment turned in past deadline, but within grace period!")
            self.grades['percentage'] = 80
        elif submission_time > self.submission_deadline:
            self.ui.notify("Assignment turned in WAY past deadline; they get a 0!")
            self.grades['percentage'] = 0

def CompileCommand(self, compile_command='make'):

    if self.args.verbose:
        print compile_command, '\n'

    ret = os.system(compile_command)
    return ret


def RunCommand(self, program_command, input_script=None):
    command = program_command
    if input_script is not None:
        command += " < %s" % input_script
    # piping with tee results in a return value of 0 always!
    command += ' > %s' % self.temp_filename
    #command += ' | tee %s' % self.temp_filename

    if self.args.verbose:
        print command, '\n'

    # for now, we're just going to assume that we won't make any changes to
    # source code: either it runs or it doesn't!
    # NOTE: we bit shift the return by one byte as the return code is actually
    # in the second byte
    return os.system(command) >> 8
    #success = False
    #while not success:
        #ret = os.system(command)
        #if ret != 0:
            #if self.ui.promptBool("Execution Failed!  Fix source code and recompile/execute?", default=True):
                #FixSource(self)
                #try:
                    #CompileCommand(self)
                #except AttributeError:
                    #if self.args.verbose:
                        #self.ui.notify('no compilation defined')
            #else:
                #success = True
        #else:
            #success = True

    #return ret

def GradeAverage(self):
    ret = CompileCommand(self, "make -f %s" % os.path.join(self.assignment_dir, "average", "Makefile"))
    if ret != 0:
        self.ui.notify("Compilation failed; skipping assignment...")
        self.grades['average'] = 0
        return

    ret = RunCommand(self, "./average %s" % os.path.join(self.assignment_dir, "numbers.dat"))
    if ret != 0:
        self.ui.notify("Error running command! Skipping assignment...")
        self.grades['average'] = 0

    # Now for grading: 40 pts possible
    score = 0
    with open(self.temp_filename) as f:
        try:
            answer = float(f.readlines()[1].strip())
            if answer == 5.5:
                score += 20
            else:
                self.grades['comments'] += "average didn't handle original input file; "
        except Exception as e:
            self.ui.notify("Error parsing: %s" % e)
            self.grades['comments'] += "Error parsing average output: %s; " % e

    RunCommand(self, "./average %s" % os.path.join(self.assignment_dir, "numbers2.dat"))
    with open(self.temp_filename) as f:
        try:
            answer = float(f.readlines()[1].strip())
            # answer should be 502.28
            if answer <= 502.35 and answer >= 502.2:
                score += 10
            else:
                self.grades['comments'] += "average didn't handle second input file with more numbers; "

        except Exception as e:
            self.ui.notify("Error parsing: %s" % e)
            self.grades['comments'] += "Error parsing average output: %s; " % e

    # check if they handle empty files properly by returning correct status
    # code
    retval = RunCommand(self, "./average %s" % os.path.join(self.assignment_dir, "numbers_blank.dat"))
    if retval == 3:
        score += 10
    else:
        self.grades['comments'] += "didn't handle blank input file properly; "

    self.grades['average'] = score


def GradeCompute(self):
    ret = CompileCommand(self) # use the makefile in this directory
    if ret != 0:
        if not self.ui.promptBool("Make failed with code %d. Continue anyway? " % ret):
            self.grades['compute'] = 0
            self.grades['comments'] += "compute didn't compile with makefile; "
            return

    score = 0
    ret = RunCommand(self, "./compute", os.path.join(self.assignment_dir, "integers.dat"))
    if ret != 0:
        if not self.ui.promptBool("Error (%d) running compute! Continue anyway? " % ret, default=True):
            self.grades['compute'] = 0
            self.grades['comments'] += "compute returned error code %d during execution with numbers.dat; " % ret
            return

    with open(self.temp_filename) as f:
        try:
            answers = f.readlines()
            theMax = float(answers[0].strip().split(":")[1])
            theMin = float(answers[1].strip().split(":")[1])
            theAvg = float(answers[2].strip().split(":")[1])

            if theMax == 100 and theMin == 10 and theAvg == 55:
                score += 20
            else:
                self.grades['comments'] += "compute output expected 100,10,55, got %d,%d,%d; " % (theMax, theMin, theAvg)

        except Exception as e:
            self.ui.notify("Error parsing: %s" % e)
            self.grades['comments'] += "error parsing compute output: %s; " % e

    ret = RunCommand(self, "./compute", os.path.join(self.assignment_dir, "integers2.dat"))
    if ret != 0:
        self.ui.notify("Error (%d) running compute!" % ret)
        self.grades['comments'] += "compute returned error code %d during execution with larger input file; " % ret

    else:
        with open(self.temp_filename) as f:
            try:
                answers = f.readlines()
                theMax = float(answers[0].strip().split(":")[1])
                theMin = float(answers[1].strip().split(":")[1])
                theAvg = float(answers[2].strip().split(":")[1])
                if theMax == 999 and theMin == 0 and theAvg == 508:
                    score += 20
                else:
                    self.grades['comments'] += "compute output expected 999,0,508, got %d,%d,%d" % (theMax, theMin, theAvg)

            except Exception as e:
                self.ui.notify("Error parsing: %s" % e)
                self.grades['comments'] += "error parsing compute output: %s; " % e

    # total can be up to 40 pts
    self.grades['compute'] = score


def ViewPart1(self, prompt=True):
    # open source files with less (I like to use the syntax highlighting lesspipe add-on)
    if not prompt or self.ui.promptBool ("View Part1?", default=True):
        os.system('less part1.txt')
    self.grades['part1'] = self.ui.promptInt("How many points did they get?", default=10)


def ViewSource(self, prompt=True):
    # open source files with less (I like to use the syntax highlighting lesspipe add-on)
    if not prompt or self.ui.promptBool ("View source?", default=False):
        os.system('less ' + self.filename)

def SubmissionSetup(self):
    self.ui.notifySubmissionSetup(self)

    self.old_dir = os.getcwd()
    os.chdir(self.submission_dir)

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

    with open(os.path.join(self.submission_dir,'.graded'), 'w') as f:
        f.write('')

    os.chdir(self.old_dir)

