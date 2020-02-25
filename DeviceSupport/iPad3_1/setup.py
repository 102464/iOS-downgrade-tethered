#!/usr/bin/env python3

import os
import time
import paramiko

import ssh


def send_kloader_and_iBSS_iBEC(sshClient: paramiko.SSHClient):
    print("Sending iBSS")
    ssh.scp_transfer_file(sshClient, os.path.abspath(".") + "/pwnediBSS", "/mnt1/pwnediBSS")
    print("Sending iBEC")
    ssh.scp_transfer_file(sshClient, os.path.abspath(".") + "/pwnediBEC", "/mnt1/pwnediBEC")
    print("Sending kloader")
    ssh.scp_transfer_file(sshClient, os.path.abspath(".") + "/tool/kloader", "/mnt1/kloader")


def createMountPoint(shell, mountpoint):
    shell.send("mkdir " + mountpoint)
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def mountDevice(shell, device, mountpoint):
    shell.send("mount -t hfs " + device + " " + mountpoint)
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def fixupvar(shell):
    shell.send("mv -v /mnt1/private/var/* /mnt2")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def copyfstab(shell):
    shell.send("cp /var/fstab /mnt1/private/etc/fstab")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def copyfstab_toSecOS(shell):
    shell.send("cp /mnt1/private/etc/fstab /var/fstab")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def unmountDevice(shell, mountpoint):
    shell.send("unmount " + mountpoint)
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break


def kloader_iBSS(shell):
    shell.send("/mnt")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break
