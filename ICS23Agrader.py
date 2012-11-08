# Agrader driver from ICS 23 Fall 2012

from os import listdir, system, getcwd, chdir, getcwd, walk, remove
from os.path import isdir, join, split, exists, getmtime
import os.path
import sys
import time

classpath_sep = ':'

def ICS23Agrader(config, args):
    #TODO: get args from config instead

    for username in sorted(listdir(join(args.dir, 'submissions'))):
        submission_dir = join(args.dir, 'submissions', username)
        # If we specified a specific set of submissions, only execute for them
        if (not args.regrade and '.graded' in listdir(submission_dir)) or (args.submissions and username not in args.submissions):
            continue

        done_grading_submission = True

        try:
            if args.verbose:
                print 'Running SubmissionSetup'
            config.SubmissionSetup(submission_dir)
        except NameError as e:
            print e
            if args.verbose:
                print 'No SubmissionSetup(submission_dir) function specified in config.'
            pass

        for program in sorted(listdir(join(args.dir, 'submissions', username))):
            dirpath = join(args.dir, 'submissions', username, program)
            if not os.path.isdir(dirpath):
                continue
            filenames = listdir(dirpath)

            if not [f.endswith('.java') for f in filenames] or dirpath.endswith('removed') or (not args.regrade and '.graded' in filenames):
                continue

            run_files = config.run_files[program]
            try:
                graded_files = config.graded_files[program]
            except AttributeError:
                graded_files = run_files

            try:
                config.PrintProgramName(program)
            except AttributeError:
                pass

            try:
                config.ProgramSetup(dirpath, run_files, graded_files)
            except NameError:
                pass

            try:
                config.CompileCommand(dirpath, run_files, graded_files)
            except NameError:
                pass

            # If the config specifies scripting inputs to the program, enumerate them
            try:
                runs = enumerate(['\n'.join([p for p in cmd_input.replace('$PATH', os.path.abspath(args.dir)).split('\n')])
                                  for cmd_input in config.cmd_inputs[program]])
            except AttributeError:
                runs = [(0,None)]

            for i,cmd_inputs in runs:
                print '\nRunning %s'% run_files
                if cmd_inputs:
                    print ' with inputs:\n%s' % cmd_inputs
                else:
                    print ''
                    
                try:
                    config.PrintExpectedOutputs(program, i)
                    print 'Expected output:\n', config.expected_outputs[program][i]
                    print '\n############################################################\nACTUAL OUTPUT'
                except AttributeError:
                    pass

                # write temp input script file if requested
                '''if cmd_inputs and not args.no_script_inputs:
                    temp_inputs_file = join(args.dir, 'inputs.tmp')
                    with open(temp_inputs_file, 'w') as f:
                        f.write(cmd_inputs)
                    run_command = run_command + ' < %s ' % temp_inputs_file'''
                
                config.RunCommand(dirpath, run_files, graded_files,verbose=args.verbose)

                if cmd_inputs and not args.no_script_inputs:
                    remove(temp_inputs_file)

                print '############################################################\n'

            #give option for viewing source code
            try:
                #if 'y' in raw_input("View source files? y/n? "):
                config.ViewSource(dirpath)
            except AttributeError:
                pass

            '''if raw_input("Grading complete? y/n? ") == 'y':
                with open(join(dirpath,'.graded'), 'w') as f:
                    f.write('')
            else:
                done_grading_submission = False'''

        # prevent entering this submission directory again if all assignments graded in it
        if done_grading_submission:
            with open(join(submission_dir,'.graded'), 'w') as f:
                f.write('')

        try:
            config.SubmissionCleanup(submission_dir)
        except NameError:
            pass
    
    try:
        config.FinalCleanup(args)
    except NameError:
        pass
