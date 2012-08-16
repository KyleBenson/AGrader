#! /usr/bin/python
usage=\
'''
Tries to populate the Google Doc gradebook roster with information from the submissions in the current (or pointed to by arg1) directory.
'''

from os import listdir
from os.path import isdir, join
from string import whitespace
from sys import argv

if len(argv) > 1:
    top_dir = argv[1]
else:
    top_dir = '.'

default_name = 'Fill In Here'

for folder in listdir(top_dir):
    if not isdir(folder) or folder == '.metadata':
        continue

    project_source = join(top_dir,folder,'src/')
    final_name = default_name
    final_stud_id = default_name
    final_ucid = default_name

    for java_file in listdir(project_source):
        if not java_file.endswith('.java'):
            continue
        
        with open(join(project_source,java_file)) as f:
        
            for line in f.readlines():
                if 'YOUR NAME: ' in line:
                    name = line.split(':')[1].strip('[]' + whitespace).title()
                    
                    #prefer longer names in case they only put first name 
                    if name != default_name or len(name) > final_name:
                        final_name = name

                elif 'YOUR STUDENT ID#: ' in line:
                    stud_id = line.split(':')[1].strip('[]' + whitespace).title()
                    if stud_id != default_name:
                        final_stud_id = stud_id

                elif 'YOUR UCINETID: ' in line:
                    ucid = line.split(':')[1].strip('[]' + whitespace).title()
                    if ucid != default_name:
                        final_ucid = ucid

                        #print folder

    '''if final_name != default_name:
        print final_name
    else:
        print folder, ' did not provide a name in java files'
        '''

    first_name,last_name = final_name.rsplit(' ',1)
    print stud_id + ',' + last_name + ',' + first_name + ',' + final_ucid 
