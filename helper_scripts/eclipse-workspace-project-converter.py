#! /usr/bin/python

ECLIPSE_WORKSPACE_PROJECT_CONVERTER_DESCRIPTION=\
'''
Searches each assignment submission (folder) in this directory (or the one specified in arg1);
if it is an Eclipse workspace (identified by looking for .metadata in it),
then move the first project in the workspace (or the one matching the second argument) 
up to replace the assignmennt submission directory (but keeping the directory's name).

It should search recursively so that it will fix conditions where the workspace is inside
of another folder.

For example:

     ./eclipse-workspace-project-converter.py ~/LabExam1/possible-workspaces

'''
from os import listdir, rename, rmdir, getcwd, walk
import os.path
from sys import argv
from shutil import rmtree, move
import difflib

def isEclipseWorkspace(path, dirs):
     '''
     Check if the current directory is an eclipse workspace by looking at the version.ini
     folder inside of the .metadata folder
     '''

     if '.metadata' in dirs and '.project' not in listdir(path):
          version_file = os.path.join(path, '.metadata', 'version.ini')
          
          if os.path.exists(version_file):
               with open(version_file) as f:
                    if 'eclipse' in f.read():
                         return True
     
     return False

def getAssignmentDirectory(top_dir, path):
     '''
     Get the proper assignment directory that is somewhere in path given
     that top_dir is the folder that contains all of the assignments.
     '''
     
     # First get the match between the two directories
     path = os.path.normpath(path)
     match = difflib.SequenceMatcher(a=path, b=top_dir).get_matching_blocks()
     match = [d for d in match if d.size and path[d.a : d.a + d.size] != os.path.sep][-1]

     diff = path[match.a + match.size :]

     # Now, pull out the first directory in, which should be the assignment since that's
     # what we expected from the user's arguments!
     diff = [d for d in diff.split(os.path.sep) if d][0]

     return os.path.join(top_dir, diff)
     
def moveAssignmentUp(assignment_name, dest, workspace, dirs):
     '''
     Move the contents of the folder specified by assignment name (or the first non-hidden one if given None)
     to the given destination folder, deleting everything else in the folder specified by path
     (including the path itself if it isn't the destination)
     '''

     if assignment_name and assignment_name not in dirs:
          print "Couldn't find assignment " + assignment_name + " in this Eclipse workspace!"
          return
     else:
          # Get first project folder
          assignment_name = [d for d in dirs if d != '.metadata'][0]
     
     dirToMove = os.path.join(workspace, assignment_name)

     print "Moving project %s in workspace %s to %s" % (assignment_name, path, assignmentDirectory)

     contents = os.listdir(dirToMove)
     for c in contents:
          move(os.path.join(dirToMove,c), os.path.join(dest, c))

     # Delete all the other contents, being careful not to kill anything we just moved
     # or the destination directory itself!
     if not os.path.samefile(os.path.abspath(workspace), os.path.abspath(dest)):
          rmtree(workspace)
     else:
          for f in os.listdir(dest):
               if f not in contents:
                    deadFile = os.path.join(dest,f)
                    if os.path.isdir(deadFile):
                         rmtree(deadFile)
                    else:
                         os.remove(deadFile)

if __name__ == '__main__':

     if len(argv) > 1:
          if '--help' == argv[1] or argv[1] == '-h':
               print ECLIPSE_WORKSPACE_PROJECT_CONVERTER_DESCRIPTION
          top_dir = argv[1]
     else:
         top_dir = '.'

     top_dir = os.path.normpath(top_dir)
     
     if len(argv) > 2:
          assignment_name = argv[2]
     else:
          assignment_name = None

     for (path, dirs, files) in walk(top_dir):
          if isEclipseWorkspace(path, dirs):
               assignmentDirectory = getAssignmentDirectory(top_dir, path)
               moveAssignmentUp(assignment_name, assignmentDirectory, path, dirs)
               dirs = [] #stop recursing
