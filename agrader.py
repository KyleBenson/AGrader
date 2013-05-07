#! /usr/bin/python

# @author: Kyle Benson
# (c) Kyle Benson 2012

AGRADER_DESCRIPTION=\
'''Loads the assignments in the specified directory.  See documentation for information about workspaces, UIs, Gradebooks, and creating Assignments.
'''

from os import listdir, system, getcwd, chdir, getcwd
from os.path import isdir, join, split, exists
from sys import argv
import sys
from getpass import getpass
#password = getpass('Enter password: ')
import argparse

# Some failsafe defaults for this version installation
# ($ Not yet supported! $)
DEFAULT_CONFIG_DIR = '~/.agrader/'
DEFAULT_CONFIG_FILE = 'config'
DEFAULT_ASSIGNMENT_FILE = 'assignment'
DEFAULT_ASSIGNMENT_DIR = '.'
DEFAULT_USERNAME = 'kebenson@uci.edu'
DEFAULT_SUBMISSION_KEY = 'ucinetid'
DEFAULT_ASSIGNMENT_KEY = 'CS143B-Project1-grades'

CRLF = '\r\n'

def ReadConfig(args):
    #TODO: try loading from assignment first?  combine multiples?
    # try loading user config file from config directory
    oldPath = sys.path[:]
    sys.path.append(args.config_dir)

    try:
        workspace = __import__(args.config_file)
    except ImportError:
        try: # it in the assignment directory
            sys.path.append(args.assignment_dir)
            workspace = __import__(args.config_file)
        except ImportError:
            #give up and get the default one
            if args.verbose:
                print 'Using default workspace'
            from Workspace import Workspace
            workspace = Workspace.GetDefault(args)
    finally:
        sys.path[:] = oldPath

    return workspace


def ParseArgs(args):
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

    # Specify assignment files/resources
    parser.add_argument('-d', '--assignment_dir', metavar='assignment_dir',
                        nargs='+', default=DEFAULT_ASSIGNMENT_DIR,
                        help='''Directory in which to find the assignment files and submissions''')
    parser.add_argument('--assignment_file', action='store', default=DEFAULT_ASSIGNMENT_FILE,
                        help='''Python file that configures the assignment (default = %(default)s)''')
    parser.add_argument('--comments', '-c', nargs='?',
                        help='''Directory in which to find text files containing canned comments''')
    parser.add_argument('--email_appendix', '-ea', nargs='?',
                        help='''File containing an appendix to include on all generated emails to students''')
    parser.add_argument('--script_inputs', action='store',
                        help='''Use the script inputs in the specified directory (their names should match the problems/assignment)''')

    #grading
    parser.add_argument('--submission_key', action='store', default=DEFAULT_SUBMISSION_KEY,
                        help='''Key used to access/submit grades for an individual submission''')
    parser.add_argument('--assignment_key', action='store', default=DEFAULT_ASSIGNMENT_KEY,
                        help='''Key used to access/submit grades for a whole assignment''')

    # Control grading flow
    parser.add_argument('--submissions', nargs='+',
                        help='''Only grade the specified submissions''')
    parser.add_argument('--problems', nargs='+',
                        help='''Only grade the specified problems''')
    parser.add_argument('--regrade', action='store_true',
                        help='''Force regrading of submissions''')

    # User preferences
    parser.add_argument('--username', action='store', default=DEFAULT_USERNAME,
                        help='''Username for logging into Gradebook, retrieving submissions, etc.''')
    parser.add_argument('--passwd', action='store', 
                        help='''Password for logging into Gradebook, retrieving submissions, etc.''')
    parser.add_argument('--verbose', action='store_true', 
                        help='''Verbosely print logging / debugging information during execution''')

    # Locations
    parser.add_argument('--config_dir', default=DEFAULT_CONFIG_DIR,
                        help='''Directory in which to find the configuration files and resources (default = %(default)s''')
    parser.add_argument('--config_file', default=DEFAULT_CONFIG_FILE,
                        help='''User's configuration file (default = %(default)s''')

    return parser.parse_args(args)


################################### MAIN ###################################
def Main():

    args = ParseArgs(argv[1:])
    workspace = ReadConfig(args)
    workspace()


if __name__ == '__main__':
    Main()
