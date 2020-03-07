#!/usr/bin/env python3

import paramiko
import time

import ssh


def restore(sshClient: paramiko.SSHClient, restoreImage, device):
    shell = sshClient.invoke_shell()
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Sending Root filesystem to your device. This may take a long time...")
    ssh.scp_transfer_file(sshClient, restoreImage, "/var/RootFilesystem.dmg")
    print("Restore new root filesystem to your partition. Please wait with patience.")
    shell.send("asr restore -source /var/RootFilesystem.dmg -target " + device + " -erase -noprompt\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        print(line.decode('utf-8'))
        if line.endswith(b'# '):
            break
    print("Restore: Done")


def formatSystem(shell):
    shell.send("newfs_hfs -s -v System -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s1\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line.endswith(b'# '):
            break
    print(line.decode('utf-8'))


def formatData(shell):
    shell.send("newfs_hfs -s -v Data -J -P -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line.endswith(b'# '):
            break
    print(line.decode('utf-8'))


def scanPartition(shell, device):
    shell.send("fsck_hfs -f " + device + "\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line.endswith(b'# '):
            break
    print(line.decode('utf-8'))

