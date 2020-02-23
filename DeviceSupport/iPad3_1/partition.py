#!/usr/bin/env python3
# Device Support for iPad3,1

import os
import time

import ioscrypto
import osinfo
import mountDevice

from biplist import *


def partitionDevice(osInfo: osinfo.OSInfo, shell, storage: int, key, iv):
    shell.send("gptfdisk\n/dev/rdisk0s1\ni\n1\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        # print(line.decode('utf-8'))
        if line:
            pos = line.decode('utf-8').find('Partition unique GUID: ')
            print("GUID position: " + str(pos))
            guid_system = line.decode('utf-8')[pos + 23:pos + 59]
            print("GUID for partition \"System\": " + guid_system)
            break
    shell.send("i\n2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        # print(line.decode('utf-8'))
        if line:
            pos = line.decode('utf-8').find('Partition unique GUID: ')
            print("GUID position: " + str(pos))
            guid_data = line.decode('utf-8')[pos + 23:pos + 59]
            print("GUID for partition \"Data\": " + guid_data)
            pos = line.decode('utf-8').find('Attribute flags: ')
            print("Attribute flags position: " + str(pos))
            attributeFlags_data: str = line.decode('utf-8')[pos + 17:pos + 33]
            print("Attribute flags for partition \"Data\": " + attributeFlags_data)
            break
    print("NOTE: These following operations won't write to disk at this moment.")
    print("Deleting partitions")
    shell.send("d\n1\nd\n2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Trying to get SystemPartitionSize from RestoreRamdisk")
    plist = readPlist(os.path.join(os.path.abspath("."), "firmware/Restore.plist"))
    print("RestoreRamdisk: " + plist['RestoreRamDisks']['User'])
    print("-> Decrypting RestoreRamdisk")
    ioscrypto.decryptImg3(osInfo, os.path.join(os.path.abspath("."),
                                               "firmware/" + plist['RestoreRamDisks']['User']),
                          os.path.abspath(".") + "/RestoreRamdisk.dmg", key, iv)
    print("-> Mounting RestoreRamdisk")
    mountDevice.mountDevice(osInfo, os.path.join(os.path.abspath("."), "RestoreRamdisk.dmg"), "mountpoint")
    plist = readPlist(os.path.join("./DeviceSupport/iPad3_1", "mountpoint/usr/local/share/restore/options.j1.plist"))
    print(plist)
    print("-> Unmounting RestoreRamdisk")
    mountDevice.unmountDevice(osInfo, "mountpoint")
    MinimumSystemPartition = plist['MinimumSystemPartition']
    print("MinimumSystemPartition: " + str(MinimumSystemPartition) + "MB")
    SystemPartitionPadding = plist['SystemPartitionPadding'][str(storage)]
    print("SystemPartitionPadding: " + str(SystemPartitionPadding) + "MB")
    SystemPartitionSize = int(MinimumSystemPartition) + int(SystemPartitionPadding)
    SystemPartitionSizeInSectors = int(SystemPartitionSize) * 1024 * 1024 / 4096
    print("   SystemPartitionSize: " + str(SystemPartitionSize) + "MB (" +
          str(int(SystemPartitionSize) * 1024 * 1024) + " in bytes)")
    print("            In Sectors: " + str(int(SystemPartitionSizeInSectors)) + " sectors")
    print("Creating new partitions")
    shell.send("n\n1\n\n" + str(int(SystemPartitionSizeInSectors)) +
               "\n\nc\n1\nSystem\nn\n2\n\n\n\nc\n2\nData\nx\na\n2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print(line.decode('utf-8'))
    print("Setting up attribute flags. FLAG=" + attributeFlags_data)
    if attributeFlags_data == "0000000000000000":
        shell.send("\n")
    elif attributeFlags_data == "0001000000000000":
        shell.send("48\n\n")
    elif attributeFlags_data == "0003000000000000":
        shell.send("48\n49\n\n")
    else:
        print("Unrecognized attribute flags for partition \"Data\".")
        print("exiting")
        exit(1)
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Setting up GUID.")
    shell.send("c\n1\n" + guid_system + "\nc\n2\n" + guid_data + "\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    # For testing purposes, I commented this.
    '''
    choice = input("WARNING: !!! Your data will ALL LOST after this operation. !!!"
                   "\nHere is a confirmation for this operation. Enter Y to continue, Enter N to abort.\n"
                   "Your choice (Make sure you know what you are doing): ")
    if choice == "Y":
        shell.send("w\nY\n")
    else:
        print("You have Entered N or other content. exiting.")
        shell.send("q\n")
        exit(1)
    '''
    shell.send("q\n")
