from Callback import RegisterCallback, RunAllCallbacks

# Base activity class that defines workflows common with many Agrader objects/activities
#
# @author: Kyle Benson
# (c) Kyle Benson 2012

class AgraderWorkflow:
    def __init__(self):
        pass

    def registerCallback(self, name, callback):
        RegisterCallback(self, 'some callback', callback)

    def runCallbacks(self, name):
        return RunAllCallbacks(self, 'some callback')
