# Gradebook base class
# @author: Kyle Benson
# (c) Kyle Benson 2012

from AGrader.AgraderWorkflow import AgraderWorkflow

class BaseGradebook(AgraderWorkflow):
    '''Provides interaction with some external gradebook service.'''

    def __init__(self, ui):
        self.ui = ui


    def submitGrades(self, grades, key):
        pass

    def getGrades(self, key):
        pass

