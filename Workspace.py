# Assignment base class
# @author: Kyle Benson
# (c) Kyle Benson 2012

from AgraderWorkflow import AgraderWorkflow
from Assignment import Assignment
from os import listdir
from sys import path

class Workspace(AgraderWorkflow):

    def __init__(self, args):
        #super(Workspace, self).__init__()
        self.ui = None
        self.gradebook = None
        self.assignments = []
        self.args = args


    __currentWorkspace = None
    @staticmethod
    def GetDefault(args=None):
        workspace = Workspace(args)

        from UI.AgraderCLUI import AgraderCLUI
        workspace.ui = AgraderCLUI(args)

        from Gradebook.Gdata import GdataSpreadsheet
        workspace.gradebook = GdataSpreadsheet(workspace.ui, args)
        
        if not Workspace.__currentWorkspace:
            Workspace.__currentWorkspace = workspace

        return workspace


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
        '''Import all of the assignments in the specified directory'''
        
        for modname in listdir(assignment_dir):
            if modname.endswith(".py"):
                if self.args.verbose:
                    self.ui.notify('Checking module %s' % modname)

                # look only in the assignment_dir directory when importing
                oldpath, path[:] = path[:], [assignment_dir]

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
                    cls = getattr(module, attr)

                    #if self.args.verbose:
                    #    self.ui.notify('Checking class %s' % attr)

                    try:
                        if issubclass(cls, Assignment) and cls is not Assignment:
                            assignments.append(cls)
                            if self.args.verbose:
                                self.ui.notify('Found assignment %s' % cls)
                    except TypeError:
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
                        if self.args.verbose:
                            self.ui.notify(e)
                        self.ui.notifyError("No submission generator for assignment module %s" % module)

                # add the assignments themselves if no submission generator
                if not generator and assignments:
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
        if self.gradebook:
            return self.gradebook.getGrades(key)
        return None