#!/usr/bin/env python3
# Device Support for iPad3,1

import os
import ioscrypto
import time

import osinfo
import mountDevice

from biplist import *


def partitionDevice(osInfo: osinfo.OSInfo, shell, key, iv):
    shell.send("gptfdisk\n/dev/rdisk0s1\ni\n1\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        # print(line.decode('utf-8'))
        if line:
            pos = line.decode('utf-8').find('Partition unique GUID: ')
            print("GUID position:" + str(pos))
            guid_system = line.decode('utf-8')[pos + 23:pos + 59]
            print("GUID for partition \"System\": " + guid_system)
            line = b''
            break
    shell.send("i\n2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        # print(line.decode('utf-8'))
        if line:
            pos = line.decode('utf-8').find('Partition unique GUID: ')
            print("GUID position:" + str(pos))
            guid_data = line.decode('utf-8')[pos + 23:pos + 59]
            print("GUID for partition \"Data\": " + guid_data)
            line = b''
            break
    print("NOTE: These following operations won't write to disk at this moment.")
    print("Deleting partitions")
    shell.send("d\n1\nd\n2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    # TODO: Mount Ramdisk and get SystemPartitionSize from plist file.
    print("Trying to get SystemPartitionSize from RestoreRamdisk")
    plist = readPlist(os.path.join(os.path.abspath("../../"), "firmware/Restore.plist"))
    print("RestoreRamdisk: " + plist['RestoreRamDisks']['User'])
    print("-> Decrypting RestoreRamdisk")
    ioscrypto.decryptImg3(osInfo, os.path.join(os.path.abspath("../../"),
                                               "firmware/" + plist['RestoreRamDisks']['User']), key, iv)
    mountDevice.mountDevice(osInfo, os.path.join(os.path.abspath("../../"),
                                                 "firmware/" + plist['RestoreRamDisks']['User'], "mountpoint"))
    print("Creating new partitions")
    shell.send("n\n1\n")
    shell.send("q\n")
