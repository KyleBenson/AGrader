#! /usr/bin/env python

# @author: Kyle Benson
# (c) Kyle Benson 2012-2015

AGRADER_DESCRIPTION=\
'''Loads the assignments in the specified directory.  See documentation for information about workspaces, UIs, Gradebooks, and creating Assignments.
'''

from os import listdir, system, getcwd, chdir, getcwd
import os.path
from os.path import isdir, join, split, exists
from sys import argv
import sys
from getpass import getpass
#password = getpass('Enter password: ')
import argparse

#TODO: not hard-code this
sys.path.append(os.path.join(os.path.expanduser('~'), 'repos'))
DEFAULT_GDATA_CREDS = os.path.join(os.path.expanduser('~'), '.gdata.creds')

# Some failsafe defaults for this version installation
# ($ Not yet supported! $)
DEFAULT_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.agrader')
DEFAULT_CONFIG_FILE = 'config'
DEFAULT_ASSIGNMENT_DIR = getcwd()
DEFAULT_ASSIGNMENT_FILE = 'assignment'
DEFAULT_USERNAME = 'kebenson@uci.edu'
DEFAULT_SUBMISSION_KEY = 'ucinetid'
DEFAULT_ASSIGNMENT_KEY = 'ICS51-Lab2-Grades'

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
            from AGrader.Workspace import Workspace
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
                        default=DEFAULT_ASSIGNMENT_DIR,
                        help='''Directory in which to find the assignment files and submissions (default = %(default)s)''')
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
    parser.add_argument('--gradebook', action='store', default='Gdata',
                        help='''Which Gradebook connector will be used (default=%(default)s).  Specifying 'none' will turn off that feature.''')

    # Control grading flow
    parser.add_argument('--submissions', nargs='+',
                        help='''Only grade the specified submissions''')
    parser.add_argument('--problems', nargs='+',
                        help='''Only grade the specified problems''')
    parser.add_argument('--regrade', action='store_true',
                        help='''Force regrading of submissions''')

    # Control UI
    parser.add_argument('--ui', metavar='interactive', action='store',
                        help='''Change the user interface. Current options are: default(clui), clui, echo, none(echo), off(none)''')

    # User preferences
    parser.add_argument('--username', action='store', default=DEFAULT_USERNAME,
                        help='''Username for logging into Gradebook, retrieving submissions, etc.''')
    parser.add_argument('--passwd', action='store', default=None,
                        help='''Password for logging into Gradebook, retrieving submissions, etc.''')
    parser.add_argument('--verbose', action='store_true',
                        help='''Verbosely print logging / debugging information during execution''')
    parser.add_argument('--gdata_creds', action='store', default=DEFAULT_GDATA_CREDS,
                        help='''OAuth2 credentials JSON file for accessing Google APIs.''')

    # Locations
    parser.add_argument('--config_dir', default=DEFAULT_CONFIG_DIR,
                        help='''Directory in which to find the configuration files and resources (default = %(default)s''')
    parser.add_argument('--config_file', default=DEFAULT_CONFIG_FILE,
                        help='''User's configuration file (default = %(default)s''')

    return_args = parser.parse_args(args)

    # set some hard values
    return_args.interactive = True
    return return_args


################################### MAIN ###################################
def Main():

    args = ParseArgs(argv[1:])
    workspace = ReadConfig(args)
    workspace()


if __name__ == '__main__':
    Main()
