#! /usr/bin/python
'''
this script reads an input roster file and converts all of the files named [student-id].txt in the submission directory
to ones named [UCINetID].txt

the roster file is not the tab-delimited one, but just the text version copy/pasted in with all columns
OTHER THAN the sid and UCINetID removed (the @uci.edu part of the email address is also removed).
the tabbed version didn't work for some reason so I just trimm the line off until we reach the start of that column.
'''

import os
import os.path
import sys

submission_dir = os.path.join(os.getcwd(), 'submissions')
roster_file = 'roster.dat'
try:
    roster_file = sys.argv[1]
except IndexError:
    pass

#open roster
with open(roster_file, 'r') as roster_file:
    for line in roster_file.readlines():
        sid = line[:8].strip()
        if '@' in line:
            ucid = line[9 : line.find('@')].strip()
        else:
            ucid = line[9:].strip()
        #print "sid: %s, ucid: %s" % (sid, ucid)

        old_filename = os.path.join(submission_dir, sid + '.txt')
        new_filename = os.path.join(submission_dir, ucid).lower()

        try:
            os.rename(old_filename, new_filename)
        except:
            #try it without extension
            old_filename_noext = os.path.splitext(old_filename)[0]
            try:
                os.rename(old_filename_noext, new_filename)
            except:
                print "didn't find expected submission file: " + old_filename
