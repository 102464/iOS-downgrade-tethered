import time
import paramiko
import socket
import subprocess
import signal

from scp import *


x = 0
ipaddr = ""
sshport = 0
sshuser = ""
sshpass = ""


def getMyIPAddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def killPort(port):
    try:
        cmd = ['lsof', '-i', ':' + port]
        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout
        output = pipe.read()
        output = str(output, encoding="utf-8")
        pid = output.split("\n")[1].split(" ")[2]
        os.kill(int(pid), signal.SIGKILL)
    except IndexError:
        print("NOTE: No process that was using port " + port)


def startUsbmuxd():
    os.system("nohup ./usbmux/tcprelay.py -t 22:2222 & >/dev/null 2>&1")
    print("Waiting for usbmux to start. Please wait for 5 seconds...")
    time.sleep(5)


def startHTTPServer():
    os.system("cd " + os.path.abspath("./debs") + "; " +
              "nohup python -m SimpleHTTPServer & >/dev/null 2>&1")
    print("Waiting for HTTP Server to start. Please wait for 5 seconds...")
    time.sleep(5)


def waitForConnection(sshobj):
    global x
    try:
        time.sleep(10)
        sshobj.connect(
            hostname="127.0.0.1",
            port=2222,
            username="root",
            password=sshpass
        )
        return sshobj
    except ConnectionError as ex:
        x = x + 1
        if x == 10:
            print("USB Connection failure: No device connected " +
                  "after 100 seconds' timeout. Exiting.")
            exit(1)
        else:
            waitForConnection(sshobj)


def setUsername(username):
    global sshuser
    sshuser = username


def setPassword(password):
    global sshpass
    sshpass = password


def setIPAndPort(ip, port = 22):
    global ipaddr, sshport
    ipaddr = ip
    sshport = port


def connect():
    ssh = paramiko.SSHClient()
    known_host = paramiko.AutoAddPolicy()
    ssh.set_missing_host_key_policy(known_host)
    ssh = waitForConnection(ssh)
    return ssh


def scp_transfer_file(ssh: paramiko.SSHClient, localpath, remotepath):
    scpClient = SCPClient(ssh.get_transport(), socket_timeout=15.0)
    try:
        scpClient.put(localpath, remotepath)
    except FileNotFoundError as e:
        print(e)
        print("Sorry, file not found:" + localpath)
        print("Exiting.")
        exit(1)
