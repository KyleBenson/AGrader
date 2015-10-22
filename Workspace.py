# Assignment base class
# @author: Kyle Benson
# (c) Kyle Benson 2012

from AGrader.AgraderWorkflow import AgraderWorkflow
from AGrader.Assignment import Assignment
from os import listdir
from sys import path

class Workspace(AgraderWorkflow):
    '''
    Singleton controller class.
    '''

    def __init__(self, args):
        #super(Workspace, self).__init__()
        self.assignments = []
        self.args = args

        # set the UI
        # do this first so that importing other functions can interact with the user
        self.ui = None
        try:
            # handle the user setting a non-interactive session
            if args.ui in ['none', 'off']:
                args.interactive = False
        except AttributeError:
            pass
        finally:
            # hard-coded default
            if self.ui is None:
                from UI.AgraderCLUI import AgraderCLUI
                self.ui = AgraderCLUI(args)

            if args is not None and not args.interactive:
                self.ui.setInteractive(False)

        # set the Gradebook
        #Gdata is the default gradebook spreadsheet
        self.gradebook = None
        if args is None or args.gradebook.lower() == 'gdata':
            from AGrader.Gradebook.Gdata import GdataSpreadsheet
            self.gradebook = GdataSpreadsheet(self.ui, args)
        elif args is not None and args.gradebook.lower() == 'file':
            from AGrader.Gradebook.FileGradebook import FileGradebook
            self.gradebook = FileGradebook(self.ui, args)
        elif args is not None and args.gradebook != 'none':
            self.ui.notifyError('Unrecognized gradebook %s. Abort?' % args.gradebook)

    __currentWorkspace = None
    @staticmethod
    def GetDefault(args=None):
        '''
        Create a default Workspace instance given the possibly specified arguments.  Will cache this instance.
        '''
        if not Workspace.__currentWorkspace:
            workspace = Workspace(args)
            Workspace.__currentWorkspace = workspace

        return Workspace.__currentWorkspace


    @staticmethod
    def GetWorkspace(id=None):
        if not Workspace.__currentWorkspace:
            Workspace.__currentWorkspace = Workspace.GetDefault()
        return  Workspace.__currentWorkspace

    def addAssignment(self, assignment):
        self.assignments.append(assignment)


    @staticmethod
    def __generateAndCallSubmissions(submission_generator, args):

        def __f__():
            for sub in submission_generator(args):
                sub()

        return __f__


    def getAssignments(self, assignment_dir):
        '''Import all of the assignments in the specified directory.
        Currently only imports the assignment specified by the argument assignment_file'''

        for modname in listdir(assignment_dir):
            # only try importing file if it's a python file and it matches the assignment file we want
            if modname.endswith(".py") and modname[:-3] == self.args.assignment_file:
                if self.args.verbose:
                    self.ui.notify('Checking module %s' % modname)

                # look also in the assignment_dir directory when importing
                oldpath, path[:] = path[:], path + [assignment_dir]

                try:
                    module = __import__(modname[:-3])
                except ImportError:
                    self.ui.notifyError("Problem importing file %s" % modname)
                    continue
                finally:    # always restore the real path
                    path[:] = oldpath

                # try loading assignments
                assignments = []
                for attr in dir(module):
                    theClass = getattr(module, attr)

                    if self.args.verbose:
                        self.ui.notify('Checking class %s' % attr)

                    try:
                        #this is a good assignment if it implements Assignment but isn't that base class itself
                        isassignment = issubclass(theClass, Assignment) and theClass is not Assignment

                        if isassignment:
                            assignments.append(theClass)
                            if self.args.verbose:
                                self.ui.notify('Found assignment %s' % theClass)
                    except TypeError as e:
                        if self.args.verbose:
                            self.ui.notify(e)
                        pass

                generator = None
                # try getting a submission generator if we found any assignments
                if assignments:
                    try:
                        generator = Workspace.__generateAndCallSubmissions(module.SubmissionGenerator, self.args)
                        #TODO: scrub some things off the args?  give some object?
                        self.addAssignment(generator)
                        if self.args.verbose:
                            self.ui.notify('Found SubmissionGenerator %s' % generator)

                    except AttributeError as e:
                        #no assignment generator
                        if self.args.verbose:
                            self.ui.notify(e)
                        self.ui.notifyError("No submission generator for assignment module %s" % module)

                        if self.args.verbose:
                            self.ui.notify('adding assignments themselves since no submission generator')
                        for a in assignments:
                            self.addAssignment(a)

        if not self.assignments:
            self.ui.notifyError("No assignments found.")

        return self.assignments


    def __call__(self):
        '''Executes the workflow.  Calls setup callbacks, runs each assignment (submitting grades after each one),
        then calls cleanup callbacks.  The callbacks take the workspace as an argument.'''

        self.runCallbacks('setup', self)

        for a in self.getAssignments(self.args.assignment_dir):
            a()

        self.runCallbacks('cleanup', self)

    def getGrades(self, key):
        '''
        Returns the gradebook associated with the given key. An empty one if the gradebook isn't connected.
        '''
        if self.gradebook:
            return self.gradebook.getGrades(key)

        if self.args.gradebook != 'none':
            self.ui.notifyError('No gradebook connected! Abort? ')
        return {} #blank gradebook if they want to continue
