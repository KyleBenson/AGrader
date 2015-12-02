import os.path, signal, shutil, sys, time, re, datetime
import subprocess
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
    # I put an 'a', 'b', etc. appended to the names for the programs they did
    program_dir = os.path.split(os.path.split(self.filename)[0])[-1]

    # filter out only the keys for this part
    # we hack on a '1) ' for each option since we request the index for changing them
    grades = {k:v for k,v in self.grades.items() if k.startswith(program_dir)}
    grades = {(str(i) + ') ' + k):v for i,(k,v) in enumerate(grades.items())}

    while True:
        self.ui.ShowGrades(grades)
        option = self.ui.promptList(sorted(grades.keys()), "Which grades would you like to correct? Leave blank when done.\n", default='')
        self.ui.notify(option)
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

    # We need to figure out the names of various files that will be generated
    # by the submission and ignore them: binary files, outputs, etc.

    #expectedFilenames = ('average', 'compute', self.temp_filename)
    #programs = ['handle_signals', 'send_signals']
    #programs = ['my_fork', 'my_shell']
    #programs = ['pthread_compute', 'mutex_compute']
    #programs = ['que']
    #programs = ['banker']
    programs = ['myls', 'mydu']
    expectedFilenames = programs + [os.path.split(self.temp_filename)[1] + '_%s' % p for p in programs]
    expectedFilenames.append('.graded')
    expectedFilenames.append('.grade_dict')

    #HW5
    #expectedFilenames.append('search.o')
    #expectedFilenames.append('que.o')

    for (dirpath, dirnames, filenames) in os.walk(self.submission_dir):
        # skip over compiled files
        t = [datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(dirpath,f))) for f in filenames if f not in expectedFilenames]
        submission_time = max(t)
        # we (may) need to remove tzinfo as the deadline has no such info
        #submission_time = submission_time.replace(tzinfo=None)

        # +10% if they submit a day early, -20% if a day late

        # used this for extra extra credit when giving a deadline extension
        #if submission_time < (self.submission_deadline - datetime.timedelta(days=2)):
            #msg = "early early submission!"
            #self.ui.notify(msg)
            #self.grades['comments'] += msg + '; '
            #self.grades['percentage'] = 120
        if submission_time < (self.submission_deadline - datetime.timedelta(days=1)):
            msg = "early submission!"
            self.ui.notify(msg)
            self.grades['comments'] += msg + '; '
            self.grades['percentage'] = 110
        elif submission_time > self.submission_deadline and submission_time < (self.submission_deadline + datetime.timedelta(days=1)):
            msg = "Assignment turned in past deadline, but within grace period!"
            self.ui.notify(msg)
            self.grades['comments'] += msg + '; '
            self.grades['percentage'] = 80
        elif submission_time > self.submission_deadline:
            self.ui.notify("Assignment turned in WAY past deadline; they get a 0!")
            self.grades['percentage'] = 0


def ReadGradesFromFile(self):
    '''Read the grades from an input file and replace the ones we read from the other Gradebook.
    Useful for transferring grades from files to Google Spreadsheets (Gdata)
    '''

    from AGrader.Gradebook.FileGradebook import FileGradebook as gb
    myGb = gb(self.ui, self.args)
    grades = myGb.getGrades(self.grade_key)

    #if not grades['comments'].startswith(self.grades['comments']):
        #if self.ui.promptBool("Comments appear out of sync.  Overwrite with those from file?", default=True):
            #self.grades['comments'] = grades['comments']
    #else:
        #self.grades['comments'] = grades['comments']


    # NOTE: the two if statements are hacks for CS143A-HW2 that allow us to do
    # some funny merging of file grades to Gdata with part1 already graded

    ## merge comments so we don't delete them
    #if 'comments' in self.grades.keys() and self.grades['comments'] is not None:
        #comments = self.grades['comments']
        #if 'comments' in grades.keys() and grades['comments'] is not None:
            #comments += grades['comments']
        #grades['comments'] = comments

    ## save scores from part1
    #if 'part1' in self.grades.keys() and self.grades['part1'] is not None:
        #grades['part1'] = self.grades['part1']
    #self.grades['part1'] = grades['part1']

    self.grades = grades


def CompileCommand(self, compile_command='make'):

    if self.args.verbose:
        self.ui.notify(compile_command)

    ret = os.system(compile_command)
    return ret


def RunCommand(self, program_command, input_script=None, output_script=None):
    command = program_command
    if input_script is not None:
        command += " < %s" % input_script
    # piping with tee results in a return value of 0 always!
    # TODO: accept problemName as an arg to avoid this hack?
    if output_script is None:
        output_script = self.temp_filename + '_%s' % program_command.replace("./","")
    command += ' > %s' % output_script
    #command += ' | tee %s' % self.temp_filename + '_%s' % problemName

    if self.args.verbose:
        self.ui.notify(command)

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
    problemName = 'average'
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
    outputFilename = self.temp_filename# + '_%s' % problemName
    with open(outputFilename) as f:
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
    with open(outputFilename) as f:
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
    problemName = 'compute'
    outputFilename = self.temp_filename# + '_%s' % problemName
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

    with open(outputFilename) as f:
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
        with open(outputFilename) as f:
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


########################################
####  SIGNALS
########################################


# seconds we expect to be able to wait before sending the next signal
global SIGNAL_SLEEP_TIME
SIGNAL_SLEEP_TIME = 0.01

# note that problemName this has to be a gdata key for grading, which can't have _s!
def problemNameToGradingKey(problemName):
    return problemName.replace('_', '')

def GradeHandleSignals(self):
    import signal
    from time import sleep

    global SIGNAL_SLEEP_TIME

    problemName = 'handle_signals'
    ret = CompileCommand(self, "gcc handle_signals.c -o handle_signals")
    if ret != 0:
        if self.ui.promptBool("Compilation failed; skip assignment? ", default=True):
            self.grades[problemNameToGradingKey(problemName)] = 0
            self.grades['comments'] += "Compilation of handle_signals.c failed with code %d" % ret
            return

    # total can be up to 50 pts
    score = 0

    with open(self.temp_filename + '_%s' % problemName, "w") as f:
        proc = subprocess.Popen("./%s" % problemName, stdout=f)

        #TODO: handle this
        ret = 0
        if ret != 0:
            if not self.ui.promptBool("Error (%d) running %s! Continue anyway? " % (problemName, ret), default=True):
                self.grades[problemNameToGradingKey(problemName)] = 0
                self.grades['comments'] += "%s returned error code %d during execution; " % (problemName, ret)
                return

        pid = proc.pid

        sleep(SIGNAL_SLEEP_TIME)
        proc.send_signal(signal.SIGQUIT)
        sleep(SIGNAL_SLEEP_TIME)
        proc.send_signal(signal.SIGINT)
        sleep(SIGNAL_SLEEP_TIME)
        proc.send_signal(signal.SIGTSTP)
        sleep(SIGNAL_SLEEP_TIME)
        proc.send_signal(signal.SIGQUIT)
        sleep(SIGNAL_SLEEP_TIME)
        proc.send_signal(signal.SIGTSTP)
        sleep(SIGNAL_SLEEP_TIME)
        proc.send_signal(signal.SIGTSTP)
        sleep(SIGNAL_SLEEP_TIME)
        proc.wait()

    with open(self.temp_filename + '_%s' % problemName) as f:
        try:
            lines = f.readlines()
            nints  = int(lines[1][len("Interrupt: "):])
            ntstps = int(lines[2][len("Stop: "):])
            nquits = int(lines[3][len("Quit: "):])
            # give points just for even attempting
            score += 10

            if nquits == 2:
	        score += 10
            else:
		self.grades['comments'] += "You didn't count SIGQUITs properly!  Probably because the \ char on the previous line commented out your increment: be more careful and check your work! got %d, expected %d; " % (nquits, 2)

	    if nints == 1:
	        score += 10
            else:
		self.grades['comments'] += "You didn't count SIGINTs properly! got %d, expected %d; " % (nints, 1)

	    if ntstps == 3:
	        score += 10
            else:
	        self.grades['comments'] += "number of SIGTSTPs not counted properly! got %d, expected %d; " % (ntstps, 3)

            if score < 40:
                # if they switched up the order of the output values, give
		# a little over half credit
                if sorted([nints, nquits, ntstps]) == [1,2,3]: # should only have 20 points here
                    score += 20
                    self.grades['comments'] += "You switched up your output values it seems.  Be more careful!; "
            else:
                score += 10 # for getting all correct

        except Exception as e:
            self.ui.notify("Error parsing: %s" % e)

            # longer sleeps may resolves this issue
            if self.ui.promptBool("Try regrading with longer sleeps? ", default=True):
                SIGNAL_SLEEP_TIME += 1
                GradeHandleSignals(self)
                return # so we don't overwrite score

            self.grades['comments'] += "error parsing %s output: %s; " % (problemName, e)
            score = 0

    self.grades[problemNameToGradingKey(problemName)] = score

    # reset this in case we changed it for problemed submissions
    SIGNAL_SLEEP_TIME = 0.01


def GradeSendSignals(self):
    import signal
    from time import sleep

    global SIGNAL_SLEEP_TIME

    problemName = 'send_signals'
    ret = CompileCommand(self, "gcc %s.c -o %s" % (problemName, problemName))
    if ret != 0:
        if self.ui.promptBool("Compilation failed; skip assignment? ", default=True):
            self.grades[problemNameToGradingKey(problemName)] = 0
            self.grades['comments'] += "Compilation of %s.c failed with code %d" % (problemName, ret)
            return

    # total can be up to 50 pts
    score = 0
    global sigsRecvd
    sigsRecvd = 0

    def sighandler(signum, frame):
        if self.args.verbose:
            self.ui.notify("Received SIGUSR2!")
        global sigsRecvd
        sigsRecvd += 1

    signal.signal(signal.SIGUSR2, sighandler)

    with open(self.temp_filename + '_%s' % problemName, "w") as f:
        proc = subprocess.Popen("./%s" % problemName, stdout=f)

        #TODO: handle proc not running

        pid = proc.pid

        sleep(SIGNAL_SLEEP_TIME)
        proc.send_signal(signal.SIGUSR1)
        sleep(SIGNAL_SLEEP_TIME)
        proc.send_signal(signal.SIGUSR1)
        sleep(SIGNAL_SLEEP_TIME)
        proc.send_signal(signal.SIGINT)
        sleep(SIGNAL_SLEEP_TIME)
        proc.wait()

    expectedAnswer = 2
    with open(self.temp_filename + '_%s' % problemName) as f:
        try:
            answer = f.readlines()[0]
            answer = int(answer.replace("Signals: ", ""))
            if answer == expectedAnswer:
                score += 20
                if answer == sigsRecvd:
                    score += 20
                else:
                    self.grades['comments'] += "Should have received %d SIGUSR2s but only got %d; " % (expectedAnswer, sigsRecvd)
            elif answer == expectedAnswer + 1:
                score += 10
                self.grades['comments'] += "Incorrect (off by 1) %s output: expected %d and got %d; " % (problemName, expectedAnswer, answer)
                if expectedAnswer == sigsRecvd:
                    score += 20
                else:
                    self.grades['comments'] += "Should have received %d SIGUSR2s but only got %d; " % (expectedAnswer, sigsRecvd)
            else:
                self.grades['comments'] += "Incorrect %s output: expected %d and got %d and received %d SIGUSR2s; " % (problemName, expectedAnswer, answer, sigsRecvd)

        except Exception as e:
            self.ui.notify("Error parsing: %s" % e)

            # longer sleeps may resolves this issue
            if self.ui.promptBool("Try regrading with longer sleeps? ", default=True):
                SIGNAL_SLEEP_TIME += 1
                GradeHandleSignals(self)
                return # so we don't overwrite score

            self.grades['comments'] += "error parsing %s output: %s; " % (problemName, e)
            score = 0

    self.grades[problemNameToGradingKey(problemName)] = score

    # reset this in case we changed it for problemed submissions
    SIGNAL_SLEEP_TIME = 0.01

def GradeMyFork(self):

    problemName = 'my_fork'

    # total can be up to 30 pts
    global score # see comment in signal handler below
    score = 0

    compiledSuccessfully, submittedMakefile, makefileCompiled = MakeProblem(self, problemName)
    if compiledSuccessfully and submittedMakefile and makefileCompiled:
        score += 5
    elif compiledSuccessfully:
        score += 3
        self.grades['comments'] += "Makefile_%s did not compile properly on openlab; " % problemName
    elif not compiledSuccessfully:
        self.grades[problemName] = 0
        return

    proc = None

    def sighandler(signum, frame):
        if self.args.verbose:
            self.ui.notify("Killing process!")
        if proc is not None:
            proc.kill()
            self.grades['comments'] += "Had to kill your my_fork: maybe it choked on k=1000?; "
            # This doesn't work in python without making it a global... feature?
            global score
            score -= 5
        else:
            sys.exit(1)

    signal.signal(signal.SIGINT, sighandler)

    # First, grade them with the default value
    argValue = 10
    expectedAnswer = 'A'*argValue + 'B'*argValue + 'C'*argValue + 'D'*argValue

    proc = subprocess.Popen("./%s" % problemName, stdout=subprocess.PIPE)
    # NOTE: we have to use communicate or the processes' competition
    # over the same file will cause lost data!
    answer, stderrdata = proc.communicate()

    try:
        try:

            # split string into chars, sort, reassemble to check
            answer = "".join(sorted(list(answer.strip())))

            if answer == expectedAnswer:
                score += 15
            else:
		# if they missed a few of the characters for some reason, partial credit
                if len(answer) > 0 and answer.replace("A", "").replace("B", "").replace("C", "").replace("D", "") == "":
		    score += 10
                self.grades['comments'] += "Your %s output was incorrect. We expected %s (not necessarilly in order) and got %s; " % (problemName, expectedAnswer, answer)

        except Exception as e:
            self.ui.notify("Error parsing: %s" % e)

            self.grades['comments'] += "error parsing %s output: %s; " % (problemName, e)
            score = 0
    except Exception as E:
        print 'this should never happen'

    # Next, grade them with a larger value
    argValue = 1000
    expectedAnswer = 'A'*argValue + 'B'*argValue + 'C'*argValue + 'D'*argValue

    proc = subprocess.Popen("./%s %d" % (problemName, argValue), stdout=subprocess.PIPE, shell=True)
    # NOTE: we have to use communicate or the processes' competition
    # over the same file will cause lost data!
    answer, stderrdata = proc.communicate()

    try:
        try:

            # split string into chars, sort, reassemble to check
            answer = "".join(sorted(list(answer.strip())))
            if answer == expectedAnswer:
                score += 10
            else:
		# if they just missed the output from some chars, partial credit
                if len(answer) > 0 and answer.replace("A", "").replace("B", "").replace("C", "").replace("D", "") == "":
                    score += 6
                self.grades['comments'] += "Your %s output was incorrect for k=%d. We expected %d total characters and got %d; " % (problemName, argValue, len(expectedAnswer), len(answer))

        except Exception as e:
            self.ui.notify("Error parsing: %s" % e)

            self.grades['comments'] += "error parsing %s output: %s; " % (problemName, e)
            score = 0
    except Exception as E:
        print 'this should never happen'

    self.grades[problemNameToGradingKey(problemName)] = score

def MakeProblem(self, problemName, makefileName=None, compileCommandStr="gcc -std=c99 -lpthread %s.c -o %s"):
    '''Try to compile the problem using make and the student's
    specified Makefile, or just use our own if possible.
    @returns - True if their file compiled successfully, else False
    '''

    # if not explicitly given, set a default value for the Makefile's name
    if makefileName is None:
        makefileName = "Makefile_%s" % problemName

    # try using the student's makefile to compile
    makefilePath = os.path.join(self.submission_dir, makefileName)
    submittedMakefile = os.path.exists(makefilePath)
    compiledSuccessfully = True
    makefileCompiled = True

    binaryName = problemName

    # Should remove output binary if it exists as otherwise we won't catch an
    # incorrect Makefile submission during regrade
    if submittedMakefile:
        os.system("make clean 2> /dev/null > /dev/null")
    elif os.path.exists(binaryName):
        os.remove(binaryName)

    if submittedMakefile:
        ret = CompileCommand(self, "make -f %s" % makefilePath)
        if ret != 0:
            makefileCompiled = False
        elif not os.path.exists(binaryName):
            self.grades['comments'] += "%s did not produce output binary %s; " % (makefileName, problemName)
            makefileCompiled = False
    if not submittedMakefile or not makefileCompiled:
        ret = CompileCommand(self, compileCommandStr % (problemName, problemName))

    if ret != 0:
        compiledSuccessfully = False
        if self.ui.promptBool("Compilation failed; give them a 0 and skip? ", default=True):
            self.grades[problemNameToGradingKey(problemName)] = 0
            self.grades['comments'] += "Compilation of %s.c failed with code %d; " % (problemName, ret)

    return compiledSuccessfully, submittedMakefile, makefileCompiled

def GradeMyShell(self):

    problemName = 'my_shell'

    # total can be up to 60 pts
    global score # see comment in signal handler below
    score = 0

    def sighandler(signum, frame):
        if self.args.verbose:
            self.ui.notify("Killing process!")
        if proc is not None:
            proc.kill()
            self.grades['comments'] += "Had to kill your shell: it should end on EOF with an input script!; "
            # This doesn't work in python without making it a global... feature?
            global score
            score -= 5
        else:
            sys.exit(1)

    signal.signal(signal.SIGINT, sighandler)

    compiledSuccessfully, submittedMakefile, makefileCompiled = MakeProblem(self, problemName)
    if compiledSuccessfully and submittedMakefile and makefileCompiled:
        score += 10
    elif compiledSuccessfully:
        self.grades['comments'] += "Makefile_%s did not compile properly on openlab; " % problemName
        score += 5
    elif not compiledSuccessfully:
        self.grades[problemName] = 0
        return


    inputScript = os.path.join(self.assignment_dir, "my_shell_script.txt")
    proc = subprocess.Popen("./%s < %s" % (problemName, inputScript), shell=True)

    #TODO: handle proc not running

    pid = proc.pid

    proc.wait()

    # Now, we want to check all the changes that should have been made by their
    # shell executing the input script and make sure it's all correct
    if os.path.exists('foo'):
        self.ui.notify("foo shouldn't exist!")
        self.grades['comments'] += "%s failed to handle more than one command appropriately; " % problemName
    elif os.path.exists('baz'):
        score += 10
    if os.path.exists('baz/foo/bar'):
        score += 10

    if os.path.exists('baz/bar'):
        score += 10
    if os.path.exists('baz/foo/bar/bar'):
        score += 5

    if os.path.exists('baz/empty'):
        score += 5
    else:
        self.grades['comments'] += "%s failed to handle empty command appropriately; " % problemName

    # the following 10 points are free if they did nothing!
    if os.path.exists('baz/blah'):
        self.ui.notify("baz/blah shouldn't exist!")
        self.grades['comments'] += "%s failed to handle invalid command appropriately; " % problemName
    else:
        score += 5

    if os.path.exists('nonsense'):
        self.ui.notify("dir nonsense shouldn't exist!")
    else:
        score += 5

    if score <= 20:
        self.grades['comments'] += "Your shell seems to have failed every command it was given; "

    self.grades[problemNameToGradingKey(problemName)] = score


def CheckForFork(self):
    problemName = 'my_fork'
    os.system("grep fork %s.c" % problemName)
    if not self.ui.promptBool("Did they use fork?", default=True):
        self.grades['comments'] += "Failed to use fork in %s!!; "

    problemName = 'my_shell'
    os.system("grep fork %s.c" % problemName)
    if not self.ui.promptBool("Did they use fork?", default=True):
        self.grades['comments'] += "Failed to use fork in %s!!; "


def GradeMutexCompute(self):
    GradePthreadCompute(self, 'mutex_compute', 40)

def GradePthreadCompute(self, problemName='pthread_compute', possibleScore=50):

    if not os.path.exists("%s.c" % problemName):
        self.grades['comments'] += "%s not submitted; " % problemName
        self.grades[problemNameToGradingKey(problemName)] = 0
        return

    global score # see comment in signal handler below
    score = 0

    compiledSuccessfully, submittedMakefile, makefileCompiled = MakeProblem(self, problemName)
    if compiledSuccessfully and submittedMakefile and makefileCompiled:
        score += 10
    elif not submittedMakefile and compiledSuccessfully:
        self.grades['comments'] += "Makefile_%s not submitted!; " % problemName
    elif compiledSuccessfully:
        score += 5
        self.grades['comments'] += "Makefile_%s did not compile properly on openlab; " % problemName
    elif not compiledSuccessfully:
        self.grades[problemNameToGradingKey(problemName)] = 0
        return

    def sighandler(signum, frame):
        if self.args.verbose:
            self.ui.notify("Killing process!")
        if proc is not None:
            proc.kill()
            self.grades['comments'] += "Had to kill your %s manually; " % problemName
            # This doesn't work in python without making it a global... feature?
            global score
            # lose 5 points for having a program that doesn't exit
            score -= 5
        else:
            sys.exit(1)

    #signal.signal(signal.SIGINT, sighandler)

    # for each combination of inputs and expected outputs,
    # we'll run the program and parse the output and build up the score
    allExpectedAnswers = [[100, 10, 55],
                          [999, 0, 508],
                          [1997, 1, 1048],
                          [999999999, 2, 250000195],
                          ]
    inputScripts = ['integers.dat', 'integers2.dat', 'integers_337.dat', 'integers_4.dat']
    for expectedAnswers, inputScript in zip(allExpectedAnswers, inputScripts):
        ret = RunCommand(self, "./%s" % problemName, os.path.join(self.assignment_dir, inputScript))
        if ret != 0:
            self.grades['comments'] += "%s returned error code %d during execution with %s; " % (problemName, ret, inputScript)
            if not self.ui.promptBool("Error (%d) running %s! Grade output anyway? " % (ret, problemName), default=True):
                continue

        with open(self.temp_filename + '_%s' % problemName) as f:
            try:
                answers = f.readlines()
                print answers, expectedAnswers
                theMax = float(answers[0].replace(" ","").strip().split(":")[1])
                theMin = float(answers[1].replace(" ","").strip().split(":")[1])
                theAvg = float(answers[2].replace(" ","").strip().split(":")[1])

                # give partial credit for each part of the answer they get right
		pointsPerAnswer = float(possibleScore - 10)/len(allExpectedAnswers)/3.0
		partsCorrect = 0
                if theMax == expectedAnswers[0]:
                    score += pointsPerAnswer
		    partsCorrect += 1
		if theMin == expectedAnswers[1]:
                    score += pointsPerAnswer
		    partsCorrect += 1
		if theAvg == expectedAnswers[2]:
                    score += pointsPerAnswer
		    partsCorrect += 1
                if partsCorrect < 3:
                    self.grades['comments'] += "%s output expected %d,%d,%d, got %.10g,%.10g,%.10g; " % ((problemName,) + tuple(expectedAnswers) + (theMax, theMin, theAvg))

            except Exception as e:
                self.ui.notify("Error parsing: %s" % e)
                self.grades['comments'] += "error parsing %s output: %s; " % (problemName, e)
        print "" # newline between executions


    self.grades[problemNameToGradingKey(problemName)] = score

def CheckForPthread(self):
    problemName = 'pthread_compute'
    os.system("grep pthread %s.c" % problemName)
    if not self.ui.promptBool("Did they use pthreads?", default=True):
        self.grades['comments'] += "Failed to use pthreads in %s!!; "
        self.grades[problemNameToGradingKey(problemName)] = 0

    problemName = 'mutex_compute'
    os.system("grep pthread %s.c" % problemName)
    if not self.ui.promptBool("Did they use pthreads?", default=True):
        self.grades['comments'] += "Failed to use pthreads in %s!!; "
        self.grades[problemNameToGradingKey(problemName)] = 0


def GradeQue(self, problemName='que', possibleScore=50):

    if not os.path.exists("%s.c" % problemName):
        self.grades['comments'] += "%s not submitted; " % problemName
        self.grades[problemNameToGradingKey(problemName)] = 0
        return

    score = 0

    ret = CompileCommand(self, "make -f %s" % os.path.join(self.args.assignment_dir, "Makefile"))
    if ret != 0:
        self.grades[problemNameToGradingKey(problemName)] = 0
        self.ui.notify("ERROR compiling! %d" % ret)
        self.grades['comments'] += "gcc returned error %d when compiling %s with Makefile; " % (ret, problemName)
        return

    # used to calculate the score based on how close it is to right answer
    def percent_error(actual, expected):
        return abs(actual - expected)/float(expected)

    # for each combination of inputs and expected outputs,
    # we'll run the program and parse the output and build up the score
    allExpectedAnswers = [5931,
                          312,
                          ]
    allArgs = ['/usr/share/dict/words',
               '~/boost/include/boost/wave/grammars/* ~/boost/include/boost/format/* ~/boost/include/boost/signals/*']
    outputFilename = self.temp_filename + '_%s' % "search"
    for expectedAnswers, args in zip(allExpectedAnswers, allArgs):
        ret = RunCommand(self, "./search the %s" % args, output_script=outputFilename)
        if ret != 0:
            self.grades['comments'] += "%s returned error code %d during execution with %s; " % (problemName, ret, args)
            if not self.ui.promptBool("Error (%d) running %s! Grade output anyway? " % (ret, problemName), default=True):
                continue

        with open(outputFilename) as f:
            try:
                answers = f.readlines()
                answer = answers[-1].strip().split(" ")
                answer = float(answer[1])

                # partial credit for close answers
                thisPossibleScore = possibleScore/len(allArgs)
                thisScore = thisPossibleScore - thisPossibleScore * percent_error(answer, expectedAnswers)
                if self.args.verbose:
                    self.ui.notify("Scored %f on %s" % (thisScore, args))

                if answer != expectedAnswers:
                    self.grades['comments'] += "%s output expected %d, got %d; " % (problemName, expectedAnswers, answer)

                score += thisScore

            except Exception as e:
                self.ui.notify("Error parsing: %s" % e)
                self.grades['comments'] += "error parsing %s output: %s; " % (problemName, e)
        print "" # newline between executions


    self.grades[problemNameToGradingKey(problemName)] = score

def GradeScheduling(self, problemName='scheduling', possibleScore=40):

    submissionFile = "part3.txt"
    if not os.path.exists(submissionFile):
        self.grades['comments'] += "%s not submitted; " % problemName
        self.grades[problemNameToGradingKey(problemName)] = 0
        return

    score = 0

    # for each combination of inputs and expected outputs,
    # we'll parse the submission file and build up the score
    allExpectedAnswers = [[91.25, 47.5],
                          [87.5, 43.75],
                          [83.75, 17.5],
                          [118.75, 11.25],
                          [87.5, 43.75],
                          ]
    pointsPerAnswer = possibleScore/2.0/len(allExpectedAnswers)

    with open(submissionFile) as f:
        for expectedAnswers, actualAnswers in zip(allExpectedAnswers, f.readlines()[:len(allExpectedAnswers)]):
            try:
                actualAnswers = actualAnswers.replace(" ","").strip().split(",")
                turnaround, response = (float(actualAnswers[0]), float(actualAnswers[1]))

                if turnaround == expectedAnswers[0]:
                    score += pointsPerAnswer
                elif turnaround == expectedAnswers[1]:
                    self.grades['comments'] += "Scheduling answers in wrong order!; "
                    score += pointsPerAnswer
                else:
                    self.grades['comments'] += "%s output expected %f, got %f; " % (problemName, expectedAnswers[0], turnaround)
                if response == expectedAnswers[1]:
                    score += pointsPerAnswer
                elif response == expectedAnswers[0]:
                    self.grades['comments'] += "Scheduling answers in wrong order!; "
                    score += pointsPerAnswer
                else:
                    self.grades['comments'] += "%s output expected %f, got %f; " % (problemName, expectedAnswers[1], response)

            except Exception as e:
                self.ui.notify("Error parsing: %s" % e)
                self.grades['comments'] += "error parsing %s output: %s; " % (problemName, e)

    self.grades[problemNameToGradingKey(problemName)] = score


def GradeBanker(self, problemName='banker', possibleScore=90):

    if not os.path.exists("%s.c" % problemName):
        self.grades['comments'] += "%s not submitted; " % problemName
        self.grades[problemNameToGradingKey(problemName)] = 0
        return

    score = 0
    makefilePoints = 10
    makefileName = 'Makefile'

    compiledSuccessfully, submittedMakefile, makefileCompiled = MakeProblem(self, problemName, makefileName=makefileName)
    if compiledSuccessfully and submittedMakefile and makefileCompiled:
        score += makefilePoints
    elif not submittedMakefile and compiledSuccessfully:
        self.grades['comments'] += "%s not submitted!; " % makefileName
    elif compiledSuccessfully:
        score += makefilePoints/2.0
        self.grades['comments'] += "%s did not compile properly on openlab; " % makefileName
    elif not compiledSuccessfully:
        self.grades[problemNameToGradingKey(problemName)] = 0
        return

    # for each combination of inputs and expected outputs,
    # we'll run the program and parse the output and build up the score
    allExpectedAnswers = ["safe", "unsafe"
                          ]
    inputScripts = ['test_safe.txt', 'test_unsafe.txt']
    pointsPerAnswer = float(possibleScore - makefilePoints)/len(inputScripts)
    for expectedAnswers, inputScript in zip(allExpectedAnswers, inputScripts):
        ret = RunCommand(self, "./%s" % problemName, os.path.join(self.assignment_dir, inputScript))
        if ret != 0:
            score -= 5
	    self.grades['comments'] += "%s returned error code %d during execution with %s: -5pts!; " % (problemName, ret, inputScript)
            if not self.ui.promptBool("Error (%d) running %s! Grade output anyway? " % (ret, problemName), default=True):
                continue

        with open(self.temp_filename + '_%s' % problemName) as f:
            try:
                answers = f.readlines()
                answer = answers[-1].strip()
                if "unsafe state" in answer:
                    if "unsafe" in inputScript:
                        score += pointsPerAnswer
                    else:
                        self.grades['comments'] += "Your program outputs that script %s is an unsafe state!; " % inputScript
                        score += pointsPerAnswer/4.0
                elif "safe state" in answer:
                    if "unsafe" not in inputScript and "safe" in inputScript:
                        score += pointsPerAnswer
                    else:
                        self.grades['comments'] += "Your program outputs that script %s is a safe state!; " % inputScript
                        score += pointsPerAnswer/4.0
                else:
                    self.grades['comments'] += "There was a problem parsing your output. Couldn't find either 'unsafe state' or 'safe state' in the last line of your output...; "

            except Exception as e:
                self.ui.notify("Error parsing: %s" % e)
                self.grades['comments'] += "error parsing %s output: %s; " % (problemName, e)
        print "" # newline between executions


    self.grades[problemNameToGradingKey(problemName)] = score

def GradeMyLs(self, problemName='myls', possibleScore=50, shellCommand="/bin/ls -lLR %s"):

    if not os.path.exists("%s.c" % problemName):
        self.grades['comments'] += "%s not submitted; " % problemName
        self.grades[problemNameToGradingKey(problemName)] = 0
        return

    makefilePoints = 5
    attemptPoints = possibleScore/2
    score = attemptPoints
    makefileName = 'Makefile_%s' % problemName

    compiledSuccessfully, submittedMakefile, makefileCompiled = MakeProblem(self, problemName, makefileName=makefileName, compileCommandStr="gcc %s.c -o %s")
    if compiledSuccessfully and submittedMakefile and makefileCompiled:
        score += makefilePoints
    elif not submittedMakefile and compiledSuccessfully:
        self.grades['comments'] += "%s not submitted!; " % makefileName
    elif compiledSuccessfully:
        score += makefilePoints/2.0
        self.grades['comments'] += "%s did not compile properly on openlab; " % makefileName
    elif not compiledSuccessfully:
        self.grades[problemNameToGradingKey(problemName)] = 0
        return

    # for each combination of inputs and expected outputs,
    # we'll run the program and parse the output and build up the score
    inputArgs = ['/bin', '/var/www']
    pointsPerAnswer = float(possibleScore - makefilePoints - attemptPoints)/len(inputArgs)
    outputFilename = os.path.join(self.assignment_dir, self.temp_filename)
    expectedOutputFilename = outputFilename + "_expected"

    for inputArg in inputArgs:
        # NOTE: we bit shift the return by one byte as the return code is actually
        # in the second byte
        ret = os.system("./%s %s > %s" % (problemName, inputArg, outputFilename)) >> 8
        if ret != 0:
            score -= 5
            self.grades['comments'] += "%s returned error code %d during execution with %s: -5pts!; " % (problemName, ret, inputArg)
            if not self.ui.promptBool("Error (%d) running %s! Grade output anyway? " % (ret, problemName), default=True):
                continue

        # this command removes the '.' that comes after the file mode bits
        # referring to some SELinux context
        expectedCommand = "%s | sed 's/^\(.[-rwsx]\{9\}\)[ \.]/\\1 /' > %s" % (shellCommand % inputArg, expectedOutputFilename)
        ret = os.system(expectedCommand) >> 8
        if ret != 0:
            self.ui.notifyError("Error executing %s! Quit?" & expectedCommand)

        # If their program passes the first diff, they get extra credit.
        # Otherwise, we'll run diff and ignore whitespace and newlines,
        # manually determining how many points they lost.
        ret = os.system("diff %s %s > /dev/null" % (outputFilename, expectedOutputFilename)) >> 8
        if ret != 0:
            os.system("diff -I GMT -I '????' -I 'mail-' -I '*.repo' -wB %s %s | less" % (outputFilename, expectedOutputFilename)) >> 8
        if ret == 0 or self.ui.promptBool("Did their output match perfectly?", default=False):
            self.ui.notify("Output matches perfectly!")
            self.grades['comments'] += "%s output matches perfectly: +5 points!; " % problemName
            score += 5 + pointsPerAnswer
        else:
            score += pointsPerAnswer - self.ui.promptInt("How many points did they lose (%d total)?" % pointsPerAnswer, default=0)
            comment = self.ui.promptStr("Want to leave a comment as to why? ", default=None)
            if comment:
                self.grades['comments'] += "%s: %s; " % (problemName, comment)

        print "" # newline between executions

    os.remove(expectedOutputFilename)

    self.grades[problemNameToGradingKey(problemName)] = score

def GradeMyDu(self, problemName='mydu', possibleScore=40, shellCommand='du %s | sort -n'):
    GradeMyLs(self, problemName, possibleScore, shellCommand)

def ViewPart1(self, prompt=True):
    # open source files with less (I like to use the syntax highlighting lesspipe add-on)
    try:
        # HW3
        #if self.grades['myfork'] == 30 and self.grades['myshell'] == 60:
        # HW4
        #if self.grades['pthreadcompute'] == 50 and self.grades['mutexcompute'] == 40:
        # HW5, etc. just check they submitted it
        if True:
            if os.path.exists('part1.txt'):
                self.ui.notify("Skipping part1 as they got 100 so far")
                self.grades['part1'] = 10
                return
            else:
                self.ui.notifyError("UNEXPECTED: got 100 on programming but no part1.txt!")
    except KeyError:
        self.ui.notifyError("UNEXPECTED: didn't find grades for other programs!")

    if not prompt or self.ui.promptBool ("View Part1?", default=True):
        os.system('less part1.txt')
    grade = self.ui.promptInt("How many points did they get?", default=10)

    if grade != 10 and prompt:
            comment = self.ui.promptStr("Want to leave a comment as to why? ", default=None)
            if comment:
                self.grades['comments'] += "Part1: %s; " % comment
    self.grades['part1'] = grade


def ViewSource(self, prompt=True):
    # open source files with less (I like to use the syntax highlighting lesspipe add-on)
    if not prompt or self.ui.promptBool ("View source?", default=False):
        os.system('less ' + self.filename)

def SubmissionSetup(self):
    self.ui.notifySubmissionSetup(self)

    self.old_dir = os.getcwd()
    os.chdir(self.submission_dir)

    # for HW3, kill the output folders
    pathsToKill = ['baz', '.temp_output_file_my_fork_10', '.temp_output_file_my_fork_1000']
    for ptk in pathsToKill:
        if os.path.isfile(ptk):
	    os.remove(ptk)
        elif os.path.exists(ptk):
	    shutil.rmtree(ptk)

    #print "Comments:", self.grades['comments']
    #if self.ui.promptBool("Reset comments?", default=True):
    #    self.grades['comments'] = ''

def clearFiles(self):
    try:
        os.remove(self.graded_file)
    except:
        pass

def SubmissionCleanup(self):
    '''Executes after running programs and viewing source'''

    if self.args.verbose:
        outputText = "\n"*2 + "\n".join(["%s: %s" % (k,v) for k,v in self.grades.iteritems()])
        self.ui.notify(outputText)

    comm = self.ui.promptStr("Leave comment for this submission?", default=None)
    if comm is not None:
        self.grades['comments'] += comm
    self.gradebook.submitGrades(self.grades, self.grade_key)

    self.ui.notifySubmissionCleanup(self)

    with open(os.path.join(self.submission_dir,'.graded'), 'w') as f:
        f.write('')

    os.chdir(self.old_dir)

