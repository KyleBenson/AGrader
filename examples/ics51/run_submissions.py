#!/usr/bin/python
from __future__ import print_function
usage = '''
Usage: run_submissions.py [dir=$PWD]
Walks through the possibly specified directory ($PWD by default), dir, recursively and compile/run each submission.
Make sure that main.cpp is in $PWD
'''

import os, sys, subprocess

def run_files(path_to_walk):
    # find every file in the current directory recursively
    for root, dirs, files in os.walk(path_to_walk):
        for f in files:
            ucinetid = f.split('.')[0]
            if f.endswith('.cpp') and not os.path.exists(ucinetid):
                compile_command = ['cl', 'main.cpp', os.path.join(root,f)]
                run_command = ['main']
                run_command.append(ucinetid)

                print(compile_command)
                print(run_command)

                if subprocess.call(compile_command):
                    input('error compiling: ' + f)
                if subprocess.call(run_command):
                    input('error running: ' + f)

if __name__ == '__main__':
    print("args: ", sys.argv)
    if len(sys.argv) < 1:
        print('Not enough arguments!\n%s' % usage)
    elif len(sys.argv) > 1:
        run_files(sys.argv[1])
    else:
        run_files(os.getcwd())
