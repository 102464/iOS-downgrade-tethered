#!/usr/bin/env python3
# Description: Device Support for iPad3,1
import paramiko
import time

import osinfo

from DeviceSupport.iPad3_1 import partition, restore


def startDowngrade(osInfo: osinfo.OSInfo, version, storage: int, sshClient: paramiko.SSHClient, keys, ivs):
    shell = sshClient.invoke_shell()
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Device Support for iPad3,1 version iOS " + version + " started")
    partition.partitionDevice_stage1(osInfo, shell, storage, keys['restoreRamdisk'], ivs['restoreRamdisk'])
    '''
    restore.formatData(shell)
    restore.formatSystem(shell)
    restore.restore(sshClient, "RootFileSystem.dmg", "/dev/disk0s1s1")
    restore.scanPartition(shell, "/dev/disk0s1s1")
    '''

if __name__ == "__main__":
    print("This is Device Support for iPad3,1. It cannot be directly executed.")
    print("Exiting")
    exit(1)
