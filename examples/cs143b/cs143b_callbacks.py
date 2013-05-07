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
    for (dirpath, dirnames, filenames) in os.walk(os.path.join(self.args.assignment_dir), 'submissions', self.name)):
        for f in filenames:
            os.system('less ' + filename)
    penalty = self.ui.promptInt("Did they lose any points for source code? ", default=0)
    self.grades['source_code'] = self.source_code_points - penalty

def GradeOutput(self):
    program_dir = os.path.split(os.path.split(self.filename)[0])[-1]

    if 'HashMap' in self.name:
        usedtrailers = False

    with open(self.filename) as f:
        expected_values = self.expected_big_oh[program_dir]
        nchecks = len(expected_values)
        nchecked = 0
        total_wrong = 0

        for line in f.readlines():
            if nchecked >= nchecks:
                if 'HashMap' in self.name:
                    line2 = line.replace(' ', '')
                    if 'newLN<K,V>(null,null)' in line2 or 'newLN(null,null)' in line2 and not line2.startswith('//'):
                        usedtrailers = True
                        break
                    else:
                        continue
                else:
                    break

            #remove all whitespace
            line = line.replace(' ', '').replace('\t','')

            if nchecked or (line.startswith('//add:') or line.startswith('//put:') and not nchecked):

                # lowercase it alland strip out * and -, then replace treeheight with logn
                # because most people just answer that way, also 2 cuz some people just silly
                massaged_line = line.replace('*','').replace('-','').replace('2','').lower().replace('treeheight', 'logn').replace('log(n)', 'logn').replace('iterables','')

                #slice off comments
                idx = massaged_line.find(')')
                if idx >= 0:
                    massaged_line = massaged_line[ : idx + 1]

                # skip over multi-line comments about big o stuff, they all look like //add:o(logn)
                if ':' not in massaged_line: #tried ':o(' but that assumes answers
                    if self.args.verbose:
                        print massaged_line
                    continue

                if massaged_line != expected_values[nchecked].lower():
                    print "Expected %s but got %s" % (expected_values[nchecked], massaged_line)
                    total_wrong += 1
                nchecked += 1
        else:
            self.ui.notify("Only checked %d in the Big-O section! Will penalize %s for that if you continue." % (nchecked, self.grade_key))
            total_wrong += nchecks - nchecked
            

    total_correct = nchecks - total_wrong

    if total_wrong:
        self.ui.notify("Total correct: %i out of %i" % (total_correct, nchecks))
    else:
        self.ui.notify("All %i Big O answers correct!" % nchecks)

    if 'HashMap' in self.name:
        self.ui.notify("They did%s use trailers. Double-check this line:\n%s" % ('' if usedtrailers else "n't", line if usedtrailers else ""))

    ViewSource(self)

    bigo_correct = self.ui.promptInt("How many did they actually get correct? ", default=total_correct)

    if 'HashMap' in self.name:
        correct = self.ui.promptBool("Did they use trailers (default = %s)? " % ('yes' if usedtrailers else 'no'),
                                     default=usedtrailers)
        if not correct:
            self.grades['usestrailerlists'] = 'X'

    #self.ui.promptContinue()
    self.grades[program_dir + 'bigo'] = str(bigo_correct)


def SubmissionSetup(self):
    self.ui.notifySubmissionSetup(self)

    SetMainMenuSignal(self)
    setsignal()

    print 'File upload times:' 

    # Check for submission deadlines and penalty for late work
    deadline_penalty = 0
    for (dirpath, dirnames, filenames) in os.walk(self.submission_dir):
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
