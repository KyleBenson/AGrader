# Assignment base class
# @author: Kyle Benson
# (c) Kyle Benson 2012

from AgraderWorkflow import AgraderWorkflow

class Workspace(AgraderWorkflow):

    def __init__(self):
        self.ui = None
        self.gradebook = None
        self.assignments = []

    def addAssignment(self, assignment):
        self.assignments.append(assignments)
        
    def run(self):
        '''Executes the workflow.  Calls setup callbacks, runs each assignment (submitting grades after each one),
        then calls cleanup callbacks.  The callbacks take the workspace as an argument.'''

        self.runCallbacks('setup', self)

        for a in self.assignments:
            a.run(self)

        self.runCallbacks('cleanup', self)
