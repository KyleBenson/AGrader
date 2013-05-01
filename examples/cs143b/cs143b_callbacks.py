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

def ProgramSetup(self):
    '''Create a link to the source file inside the package folder'''
    link_name = os.path.join(self.package_dir, os.path.split(self.filename)[-1])
    self.graded_file = link_name
    target = self.filename

    self.rungrades = {} # for RunCommand and auto-grading output

    if os.path.exists(link_name):
        os.remove(link_name)

    try:
        shutil.copyfile(target, link_name)
        #os.link(target, link_name)
    except OSError:
        self.ui.notifyError("Error linking %s to target %s!" % (link_name,target))

    ## Set main menu signaler for this assignment
        #SetMainMenuSignal(self)
    #setsignal()

def FixSource(self):
    os.system('em ' + ' '.join([self.graded_file,
                                self.run_file]))

def CompileCommand(self):
    '''Should look like:
    javac -cp .:deps/collections.jar:deps/introlib.jar:deps/junit-4.7.jar:edu/uci/ics/pattis/ics23/collections/ edu/uci/ics/pattis/ics23/collections/LinkedQueue.java
    '''

    try:
        os.remove(self.run_file.replace('.java', '.class'))
    except:
        pass
    compile_command = 'javac -cp %s %s %s' % (self.classpath, #dirpath + classpath_sep +
                                              self.run_file if os.path.exists(self.run_file) else '',
                                              self.graded_file if self.graded_file else '')

    try:
        compile_command += ' ' + self.compiled_files
    except AttributeError:
        pass

    if self.args.verbose:
        print compile_command, '\n'
        
    success = False
    while not success:
        if os.system(compile_command) != 0:
            if self.ui.promptBool("Compilation FAILED!!!!  Fix source code?", default=True):
                FixSource(self)
            else:
                success = True
        else:
            success = True


def RecordWhichFailed(self):
    for k,v in self.rungrades.iteritems():
        self.grades[k.lower()] = v

def RecordNFailed(self):
    self.grades[(os.path.split(self.dirpath)[-1] + self.name).lower()] = str(len(self.rungrades))

def RunCommand(self, input_script=None):
    '''Should look like:
    java -cp .:deps/collections.jar:deps/introlib.jar:deps/junit-4.7.jar:./edu/uci/ics/pattis/ics23/collections/ org.junit.runner.JUnitCore edu.uci.ics.pattis.ics23.collections.TestQueue
    '''
    command = 'java -cp %s %s' % (self.classpath, self.run_file)

    if input_script:
        command += ' < ' + input_script
    
    if os.path.split(self.dirpath)[-1].startswith('a'):
        command += ' | grep -v org.junit | grep -v sun.reflect'

    command += ' | tee %s' % self.temp_filename

    if self.args.verbose:
        print command, '\n'

               
    success = False
    while not success:
        ret = os.system(command)
        if ret != 0:
            if self.ui.promptBool("Execution Failed!  Fix source code and recompile/execute?", default=True):
                FixSource(self)
                try:
                    CompileCommand(self)
                except AttributeError:
                    if self.args.verbose:
                        self.ui.notify('no compilation defined')
            else:
                success = True
        else:
            success = True

    return ret

def ParseFailedTests(self):
    # parse output from JUnit tests and assign grades
    with open(self.temp_filename) as f:
        dirname = os.path.split(self.dirpath)[-1]
        current_error = 1
        line = f.readline()
        while line:
            #identify errors as starting with #) 
            error_line_start = str(current_error) + ') '
            if line.startswith(error_line_start):
                #lines look like: 1) add(edu.uci.ics.pattis.ics23.collections.TestQueue)
                function_name = dirname + line[len(error_line_start) : line.find('(')].lstrip(error_line_start).lower() #don't use just strip as it pulls off numbers
                if 'speed' in function_name:
                    line = f.readline()
                    continue

                grade = 'BX' if 'AssertionError' in f.readline() else 'RX'
                self.rungrades[function_name] = grade
                current_error += 1
                print function_name, 'failed!'

            line = f.readline()


def ViewSource(self, prompt=True):
    # open source files with less (I like to use the syntax highlighting lesspipe add-on)
    if not prompt or self.ui.promptBool ("View source?", default=False):
        os.system('less ' + self.filename)#'find ' + dirpath + ' \( -iname "*.java" \) -exec less \'{}\' +') # \'!\' -name Smiley.java \'!\' -name MusicArchive.java

def ParseGraphOutput(self, filename):
 ## Parse output file for proper printing and answers
    graph = {}
    info = {}

    # regexp: parses an edge of the form: Kansas->(79)Chicago
    edge_parser = re.compile('(\w*)\s*->\s*\((\w*)\)\s*(\w*)')
    info_parser = re.compile('(\w*)\/(\w*)\/(\w*)')

    # list of booleans about whether we parsed the correct paths/costs from their output
    paths = [False]*6

    with open(filename) as f:
        map_info_parsed_once = False # only parse distance to named dests info after we parse the graph info
        for line in f.readlines():
            # Parse their output graph
            if 'Edges' in line:
                for matches in edge_parser.findall(line[line.find('es:'):]):
                    #matches = edge_parser.match(edge.strip().replace(' ',''))
                    if len(matches) < 3:
                        self.ui.notifyError("Line %s didn't parse to give 3 pieces!" % line)
                        continue
                    source = matches[0]
                    cost = matches[1]
                    dest = matches[2]
                    
                    if source not in graph:
                        graph[source] = {}
                    graph[source][dest] = cost
                continue

            map_info_parsed = info_parser.findall(line)
            if map_info_parsed:
                map_info_parsed_once = True
                for matches in map_info_parsed:
                    if len(matches) < 3:
                        self.ui.notifyError("Line %s didn't parse to give 3 pieces!" % line)
                        continue
                    source = matches[0]
                    cost = matches[1]
                    dest = matches[2]

                    if source not in info:
                        info[source] = {}
                    info[source][dest] = cost
                continue

            # don't try to parse distance info if we ready any printed graph info or edges

            ## remove the ->'s and whitespace from the line so we can check for the paths
            line = line.translate(None, '-> ')

            if map_info_parsed_once and '99' in line:
                paths[0] = True

            elif map_info_parsed_once and '178' in line:
                paths[2] = True

            elif map_info_parsed_once and '327' in line:
                paths[4] = True

            # These 3 need to be in this order or the smaller ones would always get picked and short circuit the if/else
            if 'ChicagoKansasAtlantaMyrtleBeach' in line or 'MyrtleBeachAtlantaKansasChicago' in line:
                paths[5] = True
            
            elif 'ChicagoKansas' in line or 'KansasChicago' in line:
                paths[3] = True

            elif 'Chicago' in line and 'Node' not in line:
                paths[1] = True


    return graph, info, paths

                
def GradeGraph(self):
    # Keep them from making multiple scanners and not being able to read the scripts.
    # We replace the prompt of the TypedBufferReader with an explicit filename to prevent this
    command = '''sed -r 's/new TypedBufferReader\\s*\\("([A-Za-z ]*)"/new TypedBufferReader\("\\\\"dummy.txt"/' -i %s''' % os.path.join(self.package_dir, os.path.split(self.filename)[-1])
    if self.args.verbose:
        self.ui.notify(command)
    os.system(command)
    
    with_scripts = True
    CompileCommand(self)
    while RunCommand(self, 'input_scripts/test_source_prompt' if with_scripts else None) != 0:
        if self.ui.promptBool("Run it without scripts? "):
            with_scripts = False

    self.ui.notify('') #newline

    if not self.ui.promptBool('Did they handle checking for a source node?', default=True):
        self.grades['bbuffalo'] = 'X'

    RunCommand(self, 'input_scripts/test_dest_prompt' if with_scripts else None)

    self.ui.notify('') #newline

    if not self.ui.promptBool('Did they handle checking for a destination node?', default=True):
        self.grades['bendnode'] = 'X'

    # Switch to the other input script
    command = '''sed -r 's/dummy.txt/flightcost.txt/' -i %s''' % os.path.join(self.package_dir, os.path.split(self.filename)[-1])
    if self.args.verbose:
        self.ui.notify(command)
    os.system(command)
    
    CompileCommand(self)

    RunCommand(self, 'input_scripts/test_algorithm' if with_scripts else None)

    self.ui.notify('') #newline

    ## Parse the output files
    their_graph, their_info, their_paths = ParseGraphOutput(self, self.temp_filename)
    his_graph, his_info, his_paths = ParseGraphOutput(self, 'rich_graph_output.txt')
    
    ## Check that the maps are all the same
    correctness = []
    all_correct = True
    for source in his_graph.keys():
        for dest in his_graph[source].keys():
            correct = False
            try:
                correct = (his_graph[source][dest] == their_graph[source][dest])
            except KeyError:
                self.ui.notify("They didn't have the edge '%s->%s' in their graph" % (source, dest))

            if not correct:
                all_correct = False
                break
    correctness.append(all_correct)
    if not all_correct:
        self.grades['bprintsgraph'] = 'X'

    all_correct = True
    for source in his_info.keys():
        for dest in his_info[source].keys():
            correct = False
            try:
                correct = (his_info[source][dest] == their_info[source][dest])
            except KeyError:
                self.ui.notify("They didn't have the edge '%s->%s' in their info graph" % (source, dest))

            if not correct:
                all_correct = False
                break
    correctness.append(all_correct)
    if not all_correct:
        self.grades['bprintsinfomap'] = 'X'

    correct = their_paths[0] and their_paths[1]
    correctness.append(correct)
    if not correct:
        self.grades['bchicago'] = 'X'
    
    correct = their_paths[2] and their_paths[3]
    correctness.append(correct)
    if not correct:
        self.grades['bkansas'] = 'X'
    
    correct = their_paths[4] and their_paths[5]
    correctness.append(correct)
    if not correct:
        self.grades['bmyrtlebeach'] = 'X'

    print correctness
    correctness = (len([c for c in correctness if c]) > 1)
    print correctness
    if not correctness:
        self.ui.promptContinue("They got at most one part right.  Check if they wrote much...")
    
    ViewSource(self, prompt=False)

    # if they got nothing right, prompt for codewritten
    if not correctness:
        if not self.ui.promptBool("Did they give an honest effort at least (yes by default)?", default=True):
            self.grades['bcodewritten'] = 'X'

    CorrectGrades(self)


def GradeBigO(self):
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
    self.grades['turnedin'] = 'X'

    self.ui.notifySubmissionSetup(self)

    print 'File upload times:' 

    # Check for submission deadlines and extra credit
    extra_credit = 3
    for (dirpath, dirnames, filenames) in os.walk(self.submission_dir):
        for f,t in [(os.path.join(dirpath,f),time.localtime(os.path.getmtime(os.path.join(dirpath,f)))) for f in filenames if f.endswith('.java') and not dirpath.endswith('removed')]:
            print '%-60s \t %20s' % (f, time.asctime(t))

            if t > self.submission_deadline:
                self.ui.notify('Assignment turned in past deadline!')
                extra_credit = 0
                break
            if t > self.two_extra_credit_deadline:
                extra_credit = 0
                break
            if t > self.three_extra_credit_deadline:
                extra_credit = 2

    self.ui.notify('Extra credit: %i' % extra_credit)
    if extra_credit:
        self.grades['xcredit'] = str(extra_credit)

def clearFiles(self):
    try:
        os.remove (self.graded_file)
    except:
        pass

def SubmissionCleanup(self):
    '''Executes after running programs and viewing source'''
    partner_name = self.ui.promptStr("Enter %s's partner's name: " % self.grades['ucinetid'])
    if partner_name:
        self.grades['partnername'] = partner_name

    if self.args.verbose:
        print self.grades
    self.gradebook.submitGrades(self.grades, self.grade_key)

    self.ui.notifySubmissionCleanup(self)

    with open(os.path.join(self.submission_dir,'.graded'), 'w') as f:
        f.write('')

    # Remove all the students' compiled files
    for a in self.getAssignments():
        clearFiles(a)
    '''for f in os.listdir(self.package_dir):
    if f.endswith('.class') and 'Rich' not in f and 'TestHashMapWithSetAdapter' not in f:
    os.remove(os.path.join(self.package_dir, f))'''
    

