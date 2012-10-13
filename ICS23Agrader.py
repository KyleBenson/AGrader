# Agrader driver from ICS 23 Fall 2012

from os import listdir, system, getcwd, chdir, getcwd, walk, remove
from os.path import isdir, join, split, exists, getmtime
import os.path
import sys
import time

classpath_sep = ':'

def ReadConfig(project_dir):
    sys.path.append(project_dir)
    import project_config
    return project_config.Config(project_dir)

def ICS23Agrader(args):
    config = ReadConfig(args.dir)

    for username in sorted(listdir(join(args.dir, 'submissions'))):
        print '\n\n############################################################'
        print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n'
        print 'File upload times:' 
        for (dirpath, dirnames, filenames) in walk(join(args.dir, 'submissions', username)):
            for f,t in [(join(dirpath,f),getmtime(join(dirpath,f))) for f in filenames if f.endswith('.java') and not dirpath.endswith('removed')]:
                print f, ':', time.ctime(t)
        print '\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        print '############################################################\n\n'

        for program in sorted(listdir(join(args.dir, 'submissions', username))):
            dirpath = join(args.dir, 'submissions', username, program)
            filenames = listdir(dirpath)

            if not [f.endswith('.java') for f in filenames] or dirpath.endswith('removed') or '.graded' in filenames:
                continue

            main_class = config.main_classes[program]

            print '\n\n############################################################'
            print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n'
            print config.main_classes[program]
            print '\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
            print '############################################################\n\n'

            system('javac -cp %s %s' % (dirpath + classpath_sep + config.classpath, join(dirpath, main_class + '.java')))

            for i,cmd_inputs in enumerate(['\n'.join([p if p else p for p in cmd_input.replace('$PATH', os.path.abspath(args.dir)).split('\n')])
                                         for cmd_input in config.cmd_inputs[program]]):
                print '\nRunning %s with inputs:\n%s' % (main_class, cmd_inputs)
                print 'Expected output:'
                print config.expected_outputs[program][i]
                print '\n############################################################\nACTUAL OUTPUT'

                run_command = 'java -cp %s %s' % (dirpath + classpath_sep + config.classpath, main_class)

                if not args.no_script_inputs:
                    temp_inputs_file = join(args.dir, 'inputs.tmp')
                    with open(temp_inputs_file, 'w') as f:
                        f.write(cmd_inputs)
                    run_command = run_command + ' < %s ' % temp_inputs_file

                system(run_command)
                    
                if not args.no_script_inputs:
                    remove(temp_inputs_file)

                print '############################################################\n'

            #give option for viewing source code
            if raw_input("View source files? y/n? ") == 'y':
                system('find ' + dirpath + ' \( -iname "*.java" \) -exec less \'{}\' +') # \'!\' -name Smiley.java \'!\' -name MusicArchive.java 

            if raw_input("Grading complete? y/n? ") == 'y':
                with open(join(dirpath,'.graded'), 'w') as f:
                    f.write('')
