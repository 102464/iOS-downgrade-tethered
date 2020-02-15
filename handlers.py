import os
import sys
import signal
import serverinfo

serverpid = 0
usbmuxpid = 0


def sigint_handler(signum, frame):
    print("Signal caught, cleaning up")
    if serverpid != "":
        os.kill(int(serverpid), signal.SIGKILL)
    if usbmuxpid != "":
        os.kill(int(usbmuxpid), signal.SIGKILL)
    sys.exit(1)


def bind_handler(usbmuxdServerInfo: serverinfo.ServerInfo, httpServerInfo: serverinfo.ServerInfo):
    global serverpid, usbmuxpid
    serverpid = httpServerInfo.serverPID
    usbmuxpid = usbmuxdServerInfo.serverPID
    signal.signal(signal.SIGINT, sigint_handler)