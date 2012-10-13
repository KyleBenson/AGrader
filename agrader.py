#! /usr/bin/python

# @author: Kyle Benson
# (c) Kyle Benson 2012

AGRADER_DESCRIPTION=\
'''
Summary: ./grade-labs.py projects_directory grading_comments_directory email_appendix_file

runs through all of the directories representing Eclipse projects in the directory specified ('.' by default) and (attempts to) run the project.

Between each project, it prompts the user for a grade of pass or fail (p or f button)
and then for a reason, which is mapped to any other key as defined by the entries in the directory 'grading-reasons' or arg2 if included.

A file for a grading reason follows the following format:
a single character for a keystroke on the first line
a message to be included in the grade email.

An optional 3rd argument provides a file from which the remainder of the email comes.  Use for announcements, general observations, refined directions, etc.
'''

show_profile = False
output_connector = None
USERNAME = 'kebenson@uci.edu'
SPREADSHEET_NAME = 'ICS21-Summer2012-grades-labexams'

from os import listdir, system, getcwd, chdir, getcwd
from os.path import isdir, join, split, exists
from sys import argv
from getpass import getpass
#password = getpass('Enter password: ')
import argparse

CRLF = '\r\n'

def ParseArgs():
##################################################################################
#################      ARGUMENTS       ###########################################
# ArgumentParser.add_argument(name or flags...[, action][, nargs][, const][, default][, type][, choices][, required][, help][, metavar][, dest])
# action is one of: store[_const,_true,_false], append[_const], count
# nargs is one of: N, ?(defaults to const when no args), *, +, argparse.REMAINDER
# help supports %(var)s: help='default value is %(default)s'
##################################################################################

    parser = argparse.ArgumentParser(description=AGRADER_DESCRIPTION
                                     #formatter_class=argparse.RawTextHelpFormatter,
                                     #epilog='Text to display at the end of the help print',
                                     )

    parser.add_argument('dir',
                        help='''Directory in which to find the assignment files and submissions''')
    parser.add_argument('--comments', '-c', nargs='?',
                        help='''Directory in which to find text files containing canned comments''')
    parser.add_argument('--email-appendix', '-ea', nargs='?',
                        help='''File containing an appendix to include on all generated emails to students''')
    parser.add_argument('--no_script_inputs', '-s', action='store_true', 
                        help='''Directory in which to find text files containing canned comments''')

    return parser.parse_args()

if __name__ == '__main__':

    args = ParseArgs()

    from ICS23Agrader import *
    ICS23Agrader(args)


