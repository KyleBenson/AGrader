from Callback import RegisterCallback, RunAllCallbacks

# Base activity class that defines workflows common with many Agrader objects/activities
#
# @author: Kyle Benson
# (c) Kyle Benson 2012

class AgraderWorkflow(object):
    def __init__(self):
        pass

    def addCallback(self, name, callback):
        RegisterCallback(self, name, callback)

    def runCallbacks(self, name, *args):
        return RunAllCallbacks(self, name, *args)
