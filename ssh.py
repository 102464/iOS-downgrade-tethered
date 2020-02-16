import time
import paramiko

# TODO: Add ssh utilities here.

x = 0
ipaddr = ""
sshport = 0
sshuser = ""
sshpass = ""


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
