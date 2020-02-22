#!/usr/bin/env python3
# Description: Device Support for iPad3,1
from DeviceSupport.iPad3_1 import partition
import osinfo


def startDowngrade(osInfo: osinfo.OSInfo, version, shell, keys, ivs):
    print("Device Support for iPad3,1 version iOS " + version + " started")
    partition.partitionDevice(osInfo, shell, keys['restoreRamdisk'], ivs['restoreRamdisk'])


if __name__ == "__main__":
    print("This is Device Support for iPad3,1. It cannot be directly executed.")
    print("Exiting")
    exit(1)
