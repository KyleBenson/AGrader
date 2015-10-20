# Gradebook base class
# @author: Kyle Benson
# (c) Kyle Benson 2015

from AGrader.Gradebook.BaseGradebook import BaseGradebook

import os
import json

SAVED_FILE_NAME = ".grade_dict"

class FileGradebook(BaseGradebook):
    '''Provides interaction with a simple file-based gradebook service.'''

    def __init__(self, ui, args=None):
        super(FileGradebook, self).__init__(ui)
        self.args = args

    def submitGrades(self, grades, key):
        try:
            with open(self.getGradeFileName(key), "w") as f:
                f.write(json.dumps(grades))
        except IOError as e:
            self.ui.notifyError("couldn't write grade file %s" % SAVED_FILE_NAME)

    def getGrades(self, key):
        '''Try to read the previous grade file, otherwise return some defaults'''
        grades = {'ucinetid': key,
                  'comments': None}

        try:
            with open(self.getGradeFileName(key)) as f:
                grades = json.loads(f.read())
        except IOError as e:
            pass

        if self.args.verbose:
            self.ui.notify("Grades read: %s" % grades)
        return grades

    def getGradeFileName(self, key):
        name = os.path.join(self.args.assignment_dir, 'submissions', key, SAVED_FILE_NAME)
        return name
