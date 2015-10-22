#!/usr/bin/python
from __future__ import print_function
usage = '''
Usage: setup_submission_dirs.py manifest_file [dir=$PWD]
Walks through the possibly specified directory ($PWD by default), dir, recursively and moves each submission
to a directory all on its own. A submission is comprised of all files submitted by one student and the
directory they're moved to is named with their UCINetID. The manifest file is the .csv file emitted when
unzipping submissions downloaded from EEE.  This contains file upload information, which we use to set
the proper last modified time of the submissions in order to check for extra credit or a late penalty.
'''

import os, sys, shutil
import datetime

# Can config this script to fix submission times on already setup submission dir
MOVE_TO_DIRS=True
FIX_MOVED_SUBMISSION_TIMES=False

def setup_files(path_to_walk, manifest_file):
    # first, we need to parse the manifest file to get all the correct time
    # values for submissions
    time_info = {}
    with open(manifest_file) as f:
        for line in f.readlines():
            fileinfo = line.split(",")[-1]
            # cut out extraneous characters
            fileinfo = fileinfo.replace("(","").replace(")","").strip().replace('"','')
            # split into a 2d array where each element contains
            # (filename, timeString)
            splitdata = fileinfo.split(';')
            splitdata = [s.split(' uploaded ') for s in splitdata]
            # parse time and save it
            for (fn, t) in splitdata:
                thisTime = datetime.datetime.strptime(t, "%Y-%m-%d %I:%M%p")
                time_info[fn.strip()] = thisTime

    # find every file in the current directory recursively
    for root, dirs, files in os.walk(path_to_walk):
        if MOVE_TO_DIRS:
            for f in files:
                ucinetid = f.split('_')[0]
                submission_dirname = os.path.join(path_to_walk, ucinetid)
                new_filename = '_'.join(f.split('_')[1:])
                new_filename = os.path.join(path_to_walk, ucinetid, new_filename)
                print("Moving %s to %s" % (f, new_filename))
    
                # if we haven't made this directory yet, create it first
                if not os.path.exists(submission_dirname):
                    os.mkdir(submission_dirname)
    
                # move this file into the appropriate directory
                shutil.move(os.path.join(path_to_walk, f), new_filename)
    
        if FIX_MOVED_SUBMISSION_TIMES:
            for d in dirs:
                ucinetid = d
                for f in os.listdir(os.path.join(root, d)):
                    new_filename = os.path.join(root, d, f)
    	    	# finally, set the last modified time appropriately to reflect the
    	    	# submission upload time
                    try: # some will be compiled or AGrader files
                        theTime = int(time_info[ucinetid + "_" + f].strftime("%s"))
                        os.utime(new_filename, (theTime, theTime))
                    except KeyError:
                        continue

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Not enough arguments!\n%s' % usage)
    elif len(sys.argv) > 2:
        setup_files(sys.argv[2], sys.argv[1])
    else:
        setup_files(os.getcwd(), sys.argv[1])
