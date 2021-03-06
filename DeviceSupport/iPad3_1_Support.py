#!/usr/bin/env python3
# Description: Device Support for iPad3,1
import paramiko
import time

import osinfo

from DeviceSupport.iPad3_1 import partition, restore, setup, recovery


def startDowngrade(osInfo: osinfo.OSInfo, version, storage: int, sshClient: paramiko.SSHClient, keys, ivs):
    shell = sshClient.invoke_shell()
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Device Support for iPad3,1 version iOS " + version + " started")
    setup.createMountPoint(shell, "/mnt1")
    setup.createMountPoint(shell, "/mnt2")
    setup.mountDevice(shell, "/dev/disk0s1s1", "/mnt1")
    setup.copyfstab_toSecOS(shell)
    setup.unmountDevice(shell, "/mnt1")
    partition.partitionDevice_stage1(osInfo, shell, storage, keys['restoreRamdisk'], ivs['restoreRamdisk'])
    restore.formatData(shell)
    restore.formatSystem(shell)
    restore.restore(sshClient, "RootFileSystem.dmg", "/dev/disk0s1s1")
    # The code below hasn't been tested yet. Please stop at here!
    restore.scanPartition(shell, "/dev/disk0s1s1")
    setup.mountDevice(shell, "/dev/disk0s1s1", "/mnt1")
    setup.mountDevice(shell, "/dev/disk0s1s2", "/mnt2")
    setup.fixupvar(shell)
    setup.copyfstab(shell)
    setup.send_keybag(sshClient)
    setup.send_iBSS(sshClient)
    partition.partitionDevice_stage2(sshClient)
    partition.delete_partitions(shell)
    setup.kloader_iBSS(shell)
    sshClient.close()
    recovery.waitForConnection(osInfo)
    recovery.send_iBEC(osInfo, "pwnediBEC")
    recovery.tether_boot_up_device(osInfo)


if __name__ == "__main__":
    print("This is Device Support for iPad3,1. It cannot be directly executed.")
    print("Please run ./downgrade.py please.")
    print("Exiting")
    exit(1)
