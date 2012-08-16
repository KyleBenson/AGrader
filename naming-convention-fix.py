#! /usr/bin/python

usage = \
'''
Attempts to fix botched attampts at Alex Thornton's lab exam naming conventions.
Looks at each directory in the current one (or the one optionally specified by arg1) and
Currently does the following:

Removes occurrences of 'LabExam'
Removes brackets: [ and ]
Removes spaces
Removes occurrences of 'Attempt'

Example usage:
     ./naming-convention-fix.py ~/LabExam1
'''

from os import listdir, rename
from os.path import isdir
from sys import argv

if len(argv) > 1:
    top_dir = argv[1]
else:
    top_dir = '.'

for folder in listdir(top_dir):
    if not isdir(folder):
        continue

    folder_new = folder.replace('[','')
    folder_new = folder_new.replace(']','')
    folder_new = folder_new.replace(' ','')
    folder_new = folder_new.replace('Attempt','')
    folder_new = folder_new.replace('LabExam','')
    folder_new = folder_new.replace('labexam','')
    
    if folder_new != folder:
        #print folder_new
        rename(folder,folder_new)
