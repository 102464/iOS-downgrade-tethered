
class OSInfo:
    def __init__(self, osplatform, pythonversion):
        self.osplatform = osplatform
        self.pythonversion = pythonversion

    def getosplatform(self):
        return self.osplatform

    def getpythonversion(self):
        return self.pythonversion
