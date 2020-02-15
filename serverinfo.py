import os
import signal


class ServerType:
    # SSH = 1
    HTTP = 2
    USBMUXD = 3


class ServerInfo:
    def __init__(self, serverIP, serverType: ServerType, serverPID):
        self.serverIP = serverIP
        self.serverType = serverType
        self.serverPID = serverPID

    def getServerIP(self):
        return self.serverIP

    def getServerType(self):
        return self.serverType

    def getServerPID(self):
        return self.serverPID

    def killServer(self):
        os.kill(self.serverPID, signal.SIGKILL)
