#!/usr/bin/env python3

import os
import time
import paramiko

import ssh


def send_iBSS(sshClient: paramiko.SSHClient):
    print("Sending iBSS")
    ssh.scp_transfer_file(sshClient, os.path.abspath(".") + "/pwnediBSS", "/mnt1/pwnediBSS")


def createMountPoint(shell, mountpoint):
    print("Creating mount point " + mountpoint)
    shell.send("mkdir " + mountpoint + "\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def mountDevice(shell, device, mountpoint):
    print("Mounting " + mountpoint)
    shell.send("mount_hfs " + device + " " + mountpoint + "\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        print(line.decode('utf-8'))
        if line or line.endswith(b'# '):
            break


def fixupvar(shell):
    print("Fixing up /var")
    shell.send("mv -v /mnt1/private/var/* /mnt2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        print(line.decode('utf-8'))
        if line.endswith(b'# '):
            break


def copyfstab(shell):
    print("Copying fstab to partition.")
    shell.send("cp /var/fstab /mnt1/private/etc/fstab\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def copyfstab_toSecOS(shell):
    print("Copying fstab.")
    shell.send("cp /mnt1/private/etc/fstab /var/fstab\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def unmountDevice(shell, mountpoint):
    print("Unmounting " + mountpoint)
    shell.send("umount " + mountpoint + "\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def send_keybag(sshClient: paramiko.SSHClient):
    print("Sending keybag.")
    shell = sshClient.invoke_shell()
    shell.send("mkdir /mnt2/keybags\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break
    ssh.scp_transfer_file(sshClient, "systembag.kb", "/mnt2/keybags/systembag.kb")


def kloader_iBSS(shell):
    print("kloader iBSS!")
    shell.send("/mnt1/kloader /mnt1/pwnediBSS\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break
