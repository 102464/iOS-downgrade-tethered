#!/usr/bin/env python3
# Device Support for iPad3,1

import os
import time
import paramiko

import osinfo
import mountDevice
import ssh

from biplist import *

guid_system = ""
guid_data = ""
attributeFlags_data = ""
SystemPartitionPadding = ""


def decrypt_ramdisk(osInfo: osinfo.OSInfo, key, iv):
    print("Trying to get SystemPartitionSize from RestoreRamdisk")
    plist = readPlist(os.path.join(os.path.abspath("."), "firmware/Restore.plist"))
    print("RestoreRamdisk: " + plist['RestoreRamDisks']['User'])
    print("-> Decrypting RestoreRamdisk")
    os.system("./tools/" + osInfo.getosplatform() + "/xpwntool firmware/" +
              plist['RestoreRamDisks']['User'] + " RestoreRamdisk.dmg -k " +
              key + " -iv " + iv)


def partitionDevice_stage1(osInfo: osinfo.OSInfo, shell, storage: int, key, iv):
    global guid_data, guid_system, attributeFlags_data, SystemPartitionPadding
    shell.send("gptfdisk /dev/rdisk0s1\ni\n1\n")
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
            attributeFlags_data = line.decode('utf-8')[pos + 17:pos + 33]
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
    decrypt_ramdisk(osInfo, key, iv)
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
    # print(line.decode('utf-8'))
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
    shell.send("w\nY\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Scanning partitions.")
    shell.send("sync; sync; sync; fsck_hfs -q /dev/disk0s1s1\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break
    print(line.decode('utf-8'))
    shell.send("fsck_hfs -q /dev/disk0s1s2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break
    print(line.decode('utf-8'))
    print("Stage 1 succeed.")


def partitionDevice_stage2(sshClient: paramiko.SSHClient):
    global guid_data, guid_system, attributeFlags_data, SystemPartitionPadding
    resizedPartitionSize = 0
    shell = sshClient.invoke_shell()
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line.endswith(b'# '):
            break
    ssh.scp_transfer_file(sshClient, os.path.abspath(".") + "/firmware/kernelcache.release.j1",
                          "/mnt1/kernelcache.release.j1")
    shell.send("df -B1\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line.endswith(b'# '):
            line_stored = line
            print(line_stored.decode('utf-8'))
            break
    lines = line_stored.decode('utf-8').split('\n')
    fslist = []
    try:
        for i in lines:
            fslist.append(i.split(" "))
        for x in range(0, len(fslist) - 1):
            while '' in fslist[x]:
                fslist[x].remove('')
        for i in range(0, len(fslist) - 1):
            if fslist[i][0] == "/dev/disk0s1s1":
                print("/dev/disk0s1s1 used size is " + str(fslist[i][2]) + " bytes")
                resizedPartitionSize = int(fslist[i][2]) + int(SystemPartitionPadding) * 1024 * 1024
        if resizedPartitionSize == int(SystemPartitionPadding) * 1024 * 1024:
            print("Failed to get resized partition size")
            exit(1)
    except Exception:
        print("Unhandled exception occurred when trying to get resized partition size.")
        import traceback
        print(traceback.format_exc())
        resizedPartitionSize = int(input("Please enter it manually.\nSIZE (in bytes): "))
        print("Please make sure it is correct! Or you will fail at resizing partition!")
    print("Resized Partition Size = " + str(resizedPartitionSize))
    print("Resizing partition")
    shell.send("hfs_resize /mnt1 " + str(resizedPartitionSize) + "\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    shell.send("gptfdisk\n/dev/rdisk0s1\ni\n1\n")
    print("NOTE: These following operations won't write to disk at this moment.")
    print("Deleting partitions")
    shell.send("d\n1\nd\n2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Creating new partitions")
    SystemPartitionSizeInSectors = int(resizedPartitionSize) / 4096
    print("Sectors: " + str(int(SystemPartitionSizeInSectors)))
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
    shell.send("w\nY\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Scanning partitions.")
    shell.send("sync; sync; sync; fsck_hfs -q /dev/disk0s1s1\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line.endswith(b'# '):
            break
    print(line.decode('utf-8'))
    shell.send("fsck_hfs -q /dev/disk0s1s2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line.endswith(b'# '):
            break
    print(line.decode('utf-8'))
    print("Stage 2 succeed.")


def delete_partitions(shell):
    print("Copying hfs_resize")
    shell.send("cp /usr/bin/hfs_resize /mnt1\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line.endswith(b'# '):
            break
    print("Copying kloader")
    shell.send("cp /usr/bin/kloader /mnt1\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line.endswith(b'# '):
            break
    global guid_data, guid_system, attributeFlags_data, SystemPartitionPadding
    shell.send("gptfdisk /dev/rdisk0s1\n")
    print("NOTE: These following operations won't write to disk at this moment.")
    print("Deleting partitions")
    shell.send("d\n2\nd\n3\nd\n4\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Creating new partitions")
    shell.send("n\n2\n\n\n\nc\n2\nData\nx\na\n2\n")
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
    shell.send("c\n2\n" + guid_data + "\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print("Requesting partition size.")
    shell.send("i\n2\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            pos = line.decode('utf-8').find('Partition size: ')
            pos2 = line.decode('utf-8').find(' sectors')
            print(line.decode('utf-8')[pos+16:pos2])
            partition_size = int(line.decode('utf-8')[pos+16:pos2])
            if partition_size == 0:
                print("Failed to get partition size! Exiting")
                exit(1)
            break
    partition_size_in_bytes = partition_size * 4096
    print("Size for partition \"Data\": " + str(partition_size))
    print("                 In bytes: " + str(partition_size_in_bytes))
    shell.send("w\nY\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line:
            break
    print(line.decode('utf-8'))
    print("Partition has been deleted. The device will freeze! Don't do anything on the device!")
    print("Resizing partition")
    shell.send("/mnt1/hfs_resize /dev/disk0s1s2 " + str(partition_size_in_bytes) + "\n")
    while True:
        time.sleep(0.5)
        line = shell.recv(1024)
        if line or line.endswith(b'# '):
            break
    print("Successfully resized partition")
    print("DONE")