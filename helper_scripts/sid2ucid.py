#! /usr/bin/python
'''
this script reads an input roster file and converts all of the files named [student-id].txt in the submission directory
to ones named [UCINetID].txt

the roster file is not the tab-delimited one, but just the text version copy/pasted in.
the tabbed version didn't work for some reason so I just trimm the line off until we reach the start of that column.
'''

import os
import os.path
#import 

submission_dir = os.path.join(os.getcwd(), 'submissions')
#open roster
with open('roster.dat', 'r') as roster_file:
    for line in roster_file.readlines():
        sid = line[:8]
        ucid = line[9 : line.find('@')]
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
