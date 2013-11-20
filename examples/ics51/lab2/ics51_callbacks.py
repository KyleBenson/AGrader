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

def PrintListDifference(self, expected, actual, max_len=20):
    '''
    Prints the difference between two lists.  max_len argument (default = 20) determines space between first and second lists.
    Returns a number representing how different they are (currently the # lines that differ).  
    !!max_len currently unimplemented!!
    '''
    self.ui.notify("Expected vv but got vv")

    total_checked = total_wrong = 0

    for exp, act in zip(expected, actual):
        if exp != act:
            self.ui.notify('line %d wrong: %s %s' % (total_checked, exp, act))
            total_wrong += 1
            #self.ui.notify(('%-' + str(max_len) + 's %s') % (exp, act))
        total_checked += 1
    
    #check here for lists of unequal length
    longer_list_len = max(len(expected), len(actual))
    if longer_list_len > total_checked:
        longer_list = expected if len(expected) == longer_list_len else actual
        
        #print the remaining lines
        for val in longer_list[total_checked:]:
            self.ui.notify('unexpected value in %s: ' % ('expected' if longer_list is expected else 'actual') + str(val))
            total_wrong += 1
        
    return total_wrong

def ReadGradeFromFile(self):
    with open(self.submission) as f:
        self.grades['score'] = f.readline()

def CompareFilesByLine(self):
    with open(self.submission) as sub:
        outputs = sub.readlines()
    with open(self.expected_output_filename) as exp:
        expecteds = exp.readlines()

    self.grades['score'] = len(expecteds) - self.PrintListDifference(outputs, expecteds)

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
