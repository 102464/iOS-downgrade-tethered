#!/usr/bin/env python3

import os
import sys
import platform
import getpass
import json
import requests
import socket
import subprocess
import zipfile
import hashlib
import time
import paramiko
import signal

from scp import SCPClient
from jpype import *
from tqdm import tqdm
from urllib.request import urlopen
from biplist import *

x = 0
serverpid = ""
usbmuxpid = ""

def testssh(sshobj):
    global x
    try:
        time.sleep(10)
        sshobj.connect(
            hostname="127.0.0.1",
            port=2222,
            username="root",
            password=sshpass
        )
        return sshobj
    except:
        x = x + 1
        if x == 10:
            print("USB Connection failure: No device connected " +
                  "after 100 seconds' timeout. Exiting.")
            exit(1)
        else:
            testssh(sshobj)


def sigint_handler(signum, frame):
    print("Signal caught, cleaning up")
    if serverpid != "":
        os.kill(int(serverpid), signal.SIGKILL)
    if usbmuxpid != "":
        os.kill(int(usbmuxpid), signal.SIGKILL)
    sys.exit(1)


print("Adding SIGINT Handler")
signal.signal(signal.SIGINT, sigint_handler)
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
print("API: Downloading device information.")
if os.path.exists("firmware-api.json") == False:
    apiurl = "http://api.ipsw.me/v4"
    f = urlopen(apiurl + "/device/" + deviceidentifier + "?type=ipsw")
    with open("firmware-api.json", "wb") as code:
        code.write(f.read())
else:
    print("API: file \"firmware-api.json\" already exists. Remove for update.")
data = json.load(open("firmware-api.json"))
print("Data type: " + str(type(data)))
print("API: Getting firmware information.")
totalnum = len(data['firmwares'])
print("API: total " + str(totalnum) + " firmwares")
print(" ID               Firmware List                   ")
for i in range(0, totalnum - 1):
    print(" " + str(i + 1) + "               " + data['firmwares'][i]['version'] + " (" +
          data['firmwares'][i]['buildid'] + ")")
firmwareid = input("Enter ID: ")
if str(firmwareid).isdigit() == False:
    print("Invalid selection: Not a number. exiting.")
    exit(1)
if int(firmwareid) > totalnum or int(firmwareid) < 1:
    print("Invalid selection: Range invalid. exiting.")
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
if os.path.exists(os.path.join(os.path.abspath("."),firmwarefile))==False:
    print("Downloader: Downloading firmware")
    print("Downloader: Info")
    print("Downloader: Firmware Build " + data['firmwares'][int(firmwareid) - 1]['buildid'])
    print("Downloader:          md5hash " + md5sum)
    print("Downloader: Start downloading")
    r = requests.get(downloadlink, stream=True)
    with open(os.path.basename(downloadlink), 'wb') as f:
        file_size = int(r.headers["content-length"])
        chunk_size = 1000
        with tqdm(ncols=100, desc="Downloader: Fetching Firmware", total=file_size, unit_scale=True) as pbar:
            # 1k for chunk_size, since Ethernet packet size is around 1500 bytes
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                pbar.update(chunk_size)
    print("Downloader: Download complete")
else:
    print("Firmware already exists!")
print("Hashing firmware.")
# = hashlib.md5()
#with open(firmwarefile, "rb") as fobj:
#    while True:
#        data = fobj.read(4096)
#       if not data:
#            break
#       m.update(data)
#if m.hexdigest() != md5sum:
#    print("Firmware hash invalid! Should be " + md5sum + ", got " + m.hexdigest())
#    print("Exiting")
#    exit(1)

print("Extracting firmware...")
file = zipfile.ZipFile(firmwarefile)
#if os.path.exists(os.path.join(os.path.abspath("."),"firmware")) == False:
#    os.mkdir("firmware")
#file.extractall("firmware")
print("Successfully extracted")
print("iOSUtils: Initializing JAVA environment.")
jvm_path = getDefaultJVMPath()
print("iOSUtils: JVM Path: " + jvm_path)
if not isJVMStarted():
    startJVM(jvm_path, "-ea", "-Djava.class.path=" + os.path.join(os.path.abspath("."), "iOSUtils.jar"))
java.lang.System.out.println("If you see this message, that means JVM works well.")
print("iOSUtils: importing CA certificate")
java.lang.System.setProperty("javax.net.ssl.trustStore", "jssecacerts")
# Set keystore password
java.lang.System.setProperty("javax.net.ssl.trustStorePassword", "changeit");
# Set proxy settings (Chinese users may need that)
java.lang.System.setProperty("http.proxyHost", "127.0.0.1")
java.lang.System.setProperty("http.proxyPort", "8087")
java.lang.System.setProperty("https.proxyHost", "127.0.0.1")
java.lang.System.setProperty("https.proxyPort", "8087")
print("iOSUtils: importing JAVA class")
Utils = JClass("Utils")
KeyTypes = JClass("KeyTypes")
utils_class = Utils()
print("iOSUtils: Getting iBSS key for version " + firmwareversion + ", device " + deviceidentifier)
ibss_key = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.IBSS).getKey()
print("iOSUtils: Getting iBEC key for version " + firmwareversion + ", device " + deviceidentifier)
ibec_key = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.IBEC).getKey()
print("iOSUtils: Getting AppleLogo key for version " + firmwareversion + ", device " + deviceidentifier)
applelogo_key = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.APPLE_LOGO).getKey()
print("iOSUtils: Getting DeviceTree key for version " + firmwareversion + ", device " + deviceidentifier)
devicetree_key = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.DEVICETREE).getKey()
print("iOSUtils: Getting RootFS key for version " + firmwareversion + ", device " + deviceidentifier)
rootfs_key = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.ROOTFS).getKey()
print("iOSUtils: Getting iBSS IV for version " + firmwareversion + ", device " + deviceidentifier)
ibss_iv = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.IBSS).getIv()
print("iOSUtils: Getting iBEC IV for version " + firmwareversion + ", device " + deviceidentifier)
ibec_iv = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.IBEC).getIv()
print("iOSUtils: Getting AppleLogo IV for version " + firmwareversion + ", device " + deviceidentifier)
applelogo_iv = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.APPLE_LOGO).getIv()
print("iOSUtils: Getting DeviceTree IV for version " + firmwareversion + ", device " + deviceidentifier)
devicetree_iv = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.DEVICETREE).getIv()
print("      iBSS Key: " + ibss_key)
print("            IV: " + ibss_iv)
print("      iBEC Key: " + ibec_key)
print("            IV: " + ibec_iv)
print(" AppleLogo Key: " + applelogo_key)
print("            IV: " + applelogo_iv)
print("DeviceTree Key: " + devicetree_key)
print("            IV: " + devicetree_iv)
print("    RootFS Key: " + rootfs_key)
print("JVM: Shutdown")
shutdownJVM()
print("Next we will decrypt firmware files. Your screen will display a lot of text.")
print("That's normal! When finished, you need to connect your device with a USB cable.")
input("ENTER to continue!")
print("xpwntool: decrypting iBSS")
os.system("cd " + os.path.abspath(".") + "; " +
          "./tool/" + osplatformname + "/xpwntool ./firmware/Firmware/dfu/iBSS.*.dfu iBSS.decrypted.dfu -k " + ibss_key +
          " -iv " + ibss_iv)
print("xpwntool: decrypting iBEC")
os.system("cd " + os.path.abspath(".") + "; " +
          "./tool/" + osplatformname + "/xpwntool ./firmware/Firmware/dfu/iBEC.*.dfu iBEC.decrypted.dfu -k " + ibec_key +
          " -iv " + ibec_iv)
print("xpwntool: decrypting AppleLogo")
os.system("cd " + os.path.abspath(".") + "; " +
          "./tool/" + osplatformname + "/xpwntool ./firmware/Firmware/all_flash/*/" +
          "applelogo*.img3 applelogo.decrypted.img3 -k " + applelogo_key +
          " -iv " + applelogo_iv)
print("xpwntool: decrypting DeviceTree")
os.system("cd " + os.path.abspath(".") + "; " +
          "./tool/" + osplatformname + "/xpwntool ./firmware/Firmware/all_flash/*/" +
          "DeviceTree.*.img3 DeviceTree.decrypted.img3 -k " + devicetree_key +
          " -iv " + devicetree_iv)
print("Reading Restore.plist")
plist = readPlist("firmware/Restore.plist")
rootfsfile = plist['SystemRestoreImages']['User']
print("RootFS: " + rootfsfile)
print("Decrypting RootFileSystem")
#input("Test")
pass
newfile = rootfsfile.split(".")[0] + ".decrypted.dmg"
#os.system("cd " + os.path.abspath(".") + "; " +
#          "./tool/" + osplatformname + "/dmg extract ./firmware/" + rootfsfile + " " +
#          newfile + " -k " + rootfs_key)
if osplatformname == "macosx":
    print("hdiutil: converting format")
#    os.system("cd " + os.path.abspath(".") + "; " +
#              "hdiutil convert -format UDZO " + newfile + " -o " + rootfsfile)
    print("ASR: Scanning image")
#    ret = os.system("cd " + os.path.abspath(".") + "; " +
#                    "asr -imagescan " + rootfsfile)
#    if ret > 0:
#        print("ERROR: Image scan did not passed.")
#        print("exiting")
#        exit(ret)
if osplatformname == "linux":
    print("dmg: converting image")
    os.system("cd " + os.path.abspath(".") + "; " +
              "./tool/" + osplatformname + "/dmg build " + newfile + " " + rootfsfile)
    print("WARNING: on linux there will not be a image scan.")
    print("         please make sure image is not corrupted.")
print("iBoot32Patcher: Patching iBSS")
os.system("cd " + os.path.abspath(".") + "; " +
          "./tool/" + osplatformname + "/iBoot32Patcher iBSS.decrypted.dfu pwnediBSS")
print("iBoot32Patcher: Patching iBEC")
os.system("cd " + os.path.abspath(".") + "; " +
          "./tool/" + osplatformname + "/iBoot32Patcher iBEC.decrypted.dfu pwnediBEC -b \"rd=disk0s1s1 -v\"")
#os.remove(newfile)
print("Part II already prepared.")
print("                   PART III                       ")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
ip = s.getsockname()[0]
s.close()
os.system("cd " + os.path.abspath("./debs") + "; " +
          "nohup python -m SimpleHTTPServer & >/dev/null 2>&1")
print("Waiting for HTTP Server to start. Please wait for 5 seconds...")
time.sleep(5)
os.system("nohup ./usbmux/tcprelay.py -t 22:2222 & >/dev/null 2>&1")
print("Waiting for usbmux to start. Please wait for 5 seconds...")
time.sleep(5)
ssh = paramiko.SSHClient()
known_host = paramiko.AutoAddPolicy()
ssh.set_missing_host_key_policy(known_host)
print("Open Cydia, add source http://" + ip + ":8000, install OpenSSH, then")
cmd = ['lsof', '-i', ':8000']
pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout
output = pipe.read()
output = str(output, encoding = "utf-8")
serverpid = output.split("\n")[1].split(" ")[2]
cmd = ['lsof', '-i', ':2222']
pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout
output = pipe.read()
output = str(output, encoding = "utf-8")
usbmuxpid = output.split("\n")[1].split(" ")[2]
print("Service PID: " + serverpid)
print("Usbmux PID " + usbmuxpid)
input("Enter if finished. Ctrl-C to stop.")
print("Stopping HTTP service.")
os.kill(int(serverpid), signal.SIGKILL)
print("please connect your device with a USB cable.")
ssh = testssh(ssh)
print("Sending downgrade-required tools")
scp = SCPClient(ssh.get_transport(), socket_timeout=15)
scp.put("./debs/com.coolbooter.coolbootercli_1.1-beta1-release.deb",
        "/tmp/coolbooter.deb")
print("Installing required packages.")
ssh.exec_command("dpkg -i /tmp/coolbooter.deb")
print("CoolBooter: Installing iOS 6.1.3. This may take a long time, please wait...")
shell = ssh.invoke_shell()
while True:
    line = shell.recv(1024)
    if line and line.endswith(b'#'):
        break;
ssh.sendall("coolbootercli 6.1.3 --datasize " + str(storage / 2) + "GB")
while True:
    line = shell.recv(1024)
    if line and line.endswith(b'#'):
        break;
    print(line)
