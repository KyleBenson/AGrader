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

    def __mergeGrades(self, grades):
        return self.grades.merge(grades)
    
    def __init__(self):
        self.assignments = {}
        self.grades = {}

        
    def addAssignment(self, assignment, priority=None):
        self.assignments[assignment.name] = assignment
        self.addCallback('subassignments', assignment)
    
    def getAssignments(self):
        return self.assignments.itervalues()

    def getAssignment(self, key):
        return self.assignments[key]

    def __call__(self, parent=None):
        '''Calls setup, runs itself and then each subassignment (by calling it),
        calls any grade callbacks, then calls cleanup.'''
        
        self.runCallbacks('setup', self)
        self.runCallbacks('run', self)
        self.runCallbacks('subassignments', self)
        self.runCallbacks('grade', self)
        self.runCallbacks('cleanup', self)

