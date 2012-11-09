# Assignment base class
# @author: Kyle Benson
# (c) Kyle Benson 2012

class Assignment:
    def __init__(self, gradebook=None):
        self.gradebook = gradebook
        self.problems = []

        #ORDER???        
    def addProblem(self, problem):
        self.problems[problem.name] = problem

    def getSubmissions(self):
        pass

    def getProblems(self):
        return self.problems.itervalues()

    def getProblem(self, key):
        return self.problems[key]

    def run(self):
        for prob in self.getProblems():
            prob.run()

        self.finalize()
        
    def cleanup(self):
        pass
