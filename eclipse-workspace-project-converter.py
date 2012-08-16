#! /usr/bin/python

usage=\
'''
Searches each folder in this directory (or the one specified in arg1);
if it is an Eclipse workspace (identified by looking for .metadata in it),
  then move the first project in the workspace up one level to replace the current directory (but keeping the directory's name).

For example:

     ./eclipse-workspace-project-converter.py ~/LabExam1/possible-workspaces

'''
from os import listdir, rename, rmdir, getcwd
from os.path import isdir, join, split
from sys import argv
from shutil import rmtree, move

if len(argv) > 1:
    top_dir = argv[1]
else:
    top_dir = '.'

for folder in listdir(top_dir):
     folder = join(top_dir,folder)
     if isdir(folder) and 'LabExam2' in listdir(folder):
#'.metadata' in listdir(folder):
        #print folder
        #print join(top_dir,folder,'.metadata')
        #rmtree(join(top_dir,folder,'.metadata'))

          project_name = join(folder,'LabExam2')
          dest = split(project_name)[0]

          for i in listdir(project_name):
            #print i
               old = join(project_name,i)
               
               move(old, dest)
            #print i, isdir(i)
               
          rmdir(project_name)
