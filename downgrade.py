#!/usr/bin/env python3

# author: 102464 (https://github.com/102464)
# author: pxesrv (https://gitee.com/pxesrv) (it's also me)

import os
import sys
import platform
import getpass
import zipfile
import json
import time

import iboot
import ioscrypto
import firmwareapi
import downloader
import osinfo
import ssh

from biplist import *

print("Running System Environment Check")
ver = sys.version_info
osplatform = platform.system()
unknown = 1
print("-> Python Version: " + sys.version)
if ver < (3, 0):
    print("--> version < 3.0: Not Supported!")
    print("Exiting")
    exit(1)
print("--> version >= 3.0: Supported!")
print("-> OS Platform: " + osplatform)
if osplatform == "Darwin":
    print("--> Apple macOS: Supported!")
    unknown = 0
    osplatformname = "macosx"
if osplatform == "Windows":
    print("--> Windows Operating System: Not Supported!")
    print("exiting")
    exit(1)
if osplatform == "Linux":
    print("--> Linux: Supported!")
    osplatformname = "linux"
    unknown = 0
if unknown == 1:
    print("--> Unknown platform " + osplatform + ".")
    print("Exiting.")
    exit(1)
osInfo = osinfo.OSInfo(osplatformname, ver)
print("--------------------------------------------------")
print("Welcome to Downgrade tool.                        ")
print("This script will guide you to downgrade your      ")
print("device.                                           ")
print("This is a tethered downgrade tool. using this     ")
print("script is VERY RISKY because there are            ")
print("partitioning and restoring operation in the       ")
print("script. Please make sure there is no IMPORTANT    ")
print("DATA in your device. We won't be responsible for  ")
print("DATA LOSS and DEVICE DAMAGE when you agree using  ")
print("this script.                                      ")
print("               IMPORTANT MESSAGE                  ")
print("This is for advanced users only and the risk is   ")
print("high. If you ever slide to power off your device  ")
print("you'll be forced to restore because iBoot will    ")
print("refuse to boot the old kernel. You have been      ")
print("warned.                                           ")
print("WARNING: Some iPhone 4S and iPod touch 5 models   ")
print("don't support iOS 5 and 6 respectively due to NAND")
print("differences. If you see 'Still waiting for root   ")
print("device' error the device most likely does not     ")
print("support iOS 5/6. If you want to downgrade an      ")
print("iPhone 4S/iPod touch 5 to iOS 5/6 check           ")
print("production date before starting.                  ")
print("                  DISCLAIMER                      ")
print("           USE IT AS YOUR OWN RISK!               ")
print("--------------------------------------------------")
print("")
print("                    PART I                        ")
print("We need to gather some information.")
print("You must make sure these information are correct.")
sshpass = getpass.getpass("Enter your SSH password (Default \"alpine\", enter for default):")
if sshpass == "":
    print("Set password to Default. \"alpine\"")
    sshpass = "alpine"
else:
    print("password won't shown.")

print(" ID         SUPPORTED DEVICE LIST                 ")
print(" 1                iPad3,1                         ")
deviceidentifier = ""
devicenum = input("Enter ID: ")
if devicenum == "1":
    deviceidentifier = "iPad3,1"
else:
    print("Invalid device ID. exiting.")
    exit(1)
print(" ID                 STORAGE                       ")
print(" 1                    16G                         ")
print(" 2                    32G                         ")
print(" 3                    64G                         ")
print(" 4                   128G                         ")
storageid = input("Enter ID: ")
storage = 0
if storageid == "1":
    print("Warning! 16G devices is reported that it may have issues about free space.")
    print("         So we suggest that you should erase all data on your device.")
    print("         If you have no data on your device or you think there are enough space")
    print("         (at least 9GB), please enter Y. If you don't want to downgrade or you")
    print("         want to erase all data on your device, enter N.")
    choice = input("Y/N: ")
    if choice == "Y":
        storage = 16
    else:
        print("exiting")
        exit(1)
else:
    if storageid == "2":
        storage = 32
    else:
        if storageid == "3":
            storage = 64
        else:
            if storageid == "4":
                storage = 128
            else:
                print("Invalid selection. Exiting.")
                exit(1)
firmwareapi.getfirmwarejson(deviceidentifier)
data = json.load(open("firmware-api.json"))
print("Data type: " + str(type(data)))
print("API: Getting firmware information.")
totalnum = len(data['firmwares'])
print("API: total " + str(totalnum) + " firmwares")
print(" ID               Firmware List                   ")
num712 = 0
for i in range(0, totalnum - 1):
    print(" " + str(i + 1) + "               " + data['firmwares'][i]['version'] + " (" +
          data['firmwares'][i]['buildid'] + ")")
    if data['firmwares'][i]['version'] == "7.1.2":
        num712 = i

firmwareid = input("Enter ID: ")
if not str(firmwareid).isdigit():
    print("Invalid selection: Not a number. exiting.")
    exit(1)
if int(firmwareid) > totalnum or int(firmwareid) < 1:
    print("Invalid selection: Index out of range. exiting.")
    exit(1)
if data['firmwares'][int(firmwareid) - 1]['version'][0] == "5":
    print("iOS 5 is not supported yet! exiting.")
    exit(1)
if data['firmwares'][int(firmwareid) - 1]['version'][0] == "6":
    print("iOS 6 is not supported yet! exiting.")
    exit(1)
print("                    PART II                       ")
print("Executing pre-downgrade operation")
downloadlink = data['firmwares'][int(firmwareid) - 1]['url']
md5sum = data['firmwares'][int(firmwareid) - 1]['md5sum']
firmwareversion = data['firmwares'][int(firmwareid) - 1]['version']
firmwarefile = os.path.basename(downloadlink)
print("Download URL: " + downloadlink)
print("Checking if it is exist")
if not os.path.exists(os.path.join(os.path.abspath("."),firmwarefile)):
    print("Downloader: Downloading firmware")
    print("Downloader: Info")
    print("Downloader: Firmware Build " + data['firmwares'][int(firmwareid) - 1]['buildid'])
    print("Downloader:          md5hash " + md5sum)
    print("Downloader: Start downloading")
    downloader.download(downloadlink)
    print("Downloader: Download complete")
else:
    print("Firmware already exists!")
print("Downloading iOS 7.1.2 firmware. This is required, please wait with patience.")
firmware712 = data['firmwares'][num712]['url']
md5sum712 = data['firmwares'][num712]['md5sum']
if not os.path.exists(os.path.join(os.path.abspath("."), os.path.basename(firmware712))):
    downloader.download(firmware712)
else:
    print("Firmware already exists!")
downloader.checkHash(firmwarefile, md5sum)
downloader.checkHash(os.path.basename(firmware712), md5sum712)
print("Extracting firmware...")
file = zipfile.ZipFile(firmwarefile)
if not os.path.exists(os.path.join(os.path.abspath("."),"firmware")):
    os.mkdir("firmware")
file.extractall("firmware")
keys, ivs = ioscrypto.getKeyAndIV(firmwareversion, deviceidentifier)
print("Next we will decrypt firmware files. Your screen will display a lot of text.")
print("That's normal! When finished, you need to connect your device with a USB cable.")
input("ENTER to continue!")
ioscrypto.decryptImg3(osInfo, "firmware/Firmware/all_flash*/all_flash*/applelogo*.img3",
                      "applelogo", keys['applelogo'], ivs['applelogo'], False)
ioscrypto.decryptImg3(osInfo, "firmware/Firmware/dfu/iBSS.*.dfu", "iBSS", keys['ibss'], ivs['ibss'])
ioscrypto.decryptImg3(osInfo, "firmware/Firmware/dfu/iBEC.*.dfu", "iBEC", keys['ibec'], ivs['ibec'])
ioscrypto.decryptImg3(osInfo, "firmware/Firmware/all_flash*/all_flash*/DeviceTree.*.img3",
                      "DeviceTree", keys['devicetree'], ivs['devicetree'], False)
ioscrypto.decryptImg3(osInfo, "firmware/kernelcache.release.*", "kernelcache",
                      keys['kernelcache'], ivs['kernelcache'], False)
print("Reading Restore.plist")
plist = readPlist("firmware/Restore.plist")
rootfsfile = plist['SystemRestoreImages']['User']
print("RootFS: " + rootfsfile)
print("Decrypting RootFileSystem")
ioscrypto.decryptRootFS(osInfo, "firmware/" + rootfsfile, keys['rootfs'])
# PROBLEMS: iBSS headers always corrupts (first 16 bytes)
iboot.fix_iBSS()  # Fix the header of iBSS (first 16 bytes)
print("iBoot32Patcher: Patching iBSS")
iboot.patch_iBoot(osInfo, "iBSS", "pwnediBSS")
print("iBoot32Patcher: Patching iBEC")
iboot.patch_iBoot(osInfo, "iBEC", "iBEC.x", "rd=disk0s1s1 -v cs_enforcement_disable=1 amfi_get_out_of_my_way=1")
print("Repacking iBEC")
# ioscrypto.repackImg3(osInfo, "iBSS.x", "pwnediBSS", "ibss") iBSS doesn't need to be repacked.
ioscrypto.repackImg3(osInfo, "iBEC.x", "pwnediBEC", "ibec")
print("Part II already prepared.")
print("                   PART III                       ")
ssh.killPort(2222)
ssh.killPort(8000)
ssh.setPassword(sshpass)
ssh.setIPAndPort("127.0.0.1", "2222")
ssh.setUsername("root")
ssh.startUsbmuxd()
ssh.startHTTPServer()

ip = ssh.getMyIPAddress()
print("Open Cydia, add source http://" + ip + ":8000, install OpenSSH and CoolBooter, then")
print("please connect your device with a USB cable.")
input("Enter if finished. Ctrl-C to stop.")
print("Stopping HTTP service.")
ssh.killPort(8000)
print("---[Waiting for connection]---")
sshClient = ssh.connect()
print("Please remove passcode lock before continue. Passcode may cause bootloop on this device.")
input("ENTER TO CONTINUE.")
print("Backing up keybag.")

ssh.scp_get_file(sshClient, "/var/keybags/systembag.kb", "systembag.kb")
print("Sending iOS 6.1.3 firmware. This may need a long time...")
sshClient.exec_command("mkdir /var/cbooter")
ssh.scp_transfer_file(sshClient, os.path.basename(firmware712),
                      "/var/cbooter/" + os.path.basename(firmware712))
print("CoolBooter: Installing iOS 7.1.2, please wait...")
shell = sshClient.invoke_shell()
while True:
    line = shell.recv(1024)
    if line:
        break
shell.send("coolbootercli 7.1.2 --datasize " + str(int(storage / 2)) + "GB\n")
while True:
    line = shell.recv(1024)
    print(line.decode('utf-8'))
    if line == b'':
        break
print("Device should automatically reboots. Wait 80 seconds...")
time.sleep(80)
input("Start SSH Service and ENTER TO CONTINUE")

print("---[Waiting for connection]---")
sshClient = ssh.connect()
shell = sshClient.invoke_shell()
print("Rebooting your device to new system. Please lock your device after 5 seconds.")
shell.send("coolbootercli -b\n")
time.sleep(5)
print("Lock your device to continue.")
while True:
    line = shell.recv(1024)
    print(line.decode('utf-8'))
    if line == b'':
        print("multi_kloader ends")
        print("Device should boot in verbose mode. If not, press any hardware button "
              "(like home button).")
        break
sshClient.close()
print("Waiting for a minute for your device to start...")
time.sleep(60)
print("End Part III.")
print("                    PART IV                        ")
ssh.startHTTPServer()
print("Open Cydia, add source http://" + ip + ":8000, install OpenSSH, diskdev-cmds, and dualbootstuff.")
input("Enter if finished. Ctrl-C to stop.")
print("Stopping HTTP service.")
ssh.killPort(8000)
print("--[Waiting for connection]---")
sshClient = ssh.connect()
print("+----------------------------[ D A N G E R ]----------------------------+")
print("| DANGER! You have entered the most dangerous part.                     |")
print("| We will partition this device and restore the firmware                |")
print("| to device. The device may BRICK at any time and data cannot           |")
print("| be recovered. If your device bricks or entered boot loop,             |")
print("| please manually let your device enter DFU mode, and restore           |")
print("| it using iTunes.                                                      |")
print("| Your data will ALL LOST after downgrading with this tool!             |")
print("+-----------------------------------------------------------------------+")
print("")
input("ENTER TO CONTINUE. Ctrl-C to abort.")

if deviceidentifier == 'iPad3,1':
    from DeviceSupport import iPad3_1_Support
    print("Starting downgrade process.")
    iPad3_1_Support.startDowngrade(osInfo, firmwareversion, storage, sshClient, keys, ivs)

print("Congratulations, Your device has been successfully booted.")
print("Note: If you want to enable \"Slide to power off\", Install MakeItTethered in debs/ directory.")
print("ENJOY YOUR DOWNGRADED DEVICE!")
print("---[END]---")

exit(0)
