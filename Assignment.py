# Assignment base class
#
# @author: Kyle Benson
# (c) Kyle Benson 2012

from AgraderWorkflow import AgraderWorkflow

class Assignment(AgraderWorkflow):
    '''Represents a single assignment (or submassignment) in the view of a single submission,
    being possibly composed of different subassignments.
    
    Supports several categories of callbacks (each of which accepts the assignment as an argument):
    setup: runs at the beginning of a assignment
    cleanup: runs after grading all the subassignments
    grade: run when gathering grades for a submission
    '''
    
    def __init__(self):
        self.assignments = {}
        self.grades = {}
        
    def addAssignment(self, assignment):
        self.assignments[assignment.name] = assignment
    
    def getAssignments(self):
        return self.assignments.itervalues()

    def getAssignment(self, key):
        return self.assignments[key]

    def run(self, parent=None):
        '''Calls setup, runs each assignment by calling its run method
        and then calling any grade callbacks, then calls cleanup.'''

        self.runCallbacks('setup', self)

        for a in self.getAssignments():
            a.run(self)
            self.runCallbacks('grade', a)

        self.runCallbacks('cleanup', self)

    def getGrades(self):
        return self.grades

