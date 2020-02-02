import os
import platform
import getpass
import json
import requests
import jpype
from tqdm import tqdm
from urllib.request import urlopen

ua = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

print("Running System Environment Check")
osplatform = platform.system()
unknown = 1
print("-> OS Platform: " + osplatform)
if osplatform == "Darwin":
    print("--> Apple OSX: Supported!")
    unknown = 0 
if osplatform == "Windows":
    print("--> Windows Operating System: Not Supported!")
    print("exiting")
    exit(1)
if osplatform == "Linux":
    print("--> Linux: Supported!")
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
print("DATA in your device. We won't be responible for   ")
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
    print(" " + str(i + 1) + "                   " + data['firmwares'][i]['version'])
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
print("Continuing.")
downloadlink = data['firmwares'][int(firmwareid) - 1]['url']
md5sum = data['firmwares'][int(firmwareid) - 1]['md5sum']
print("Download URL: " + downloadlink)
print("Downloader: Downloading firmware")
print("Downloader: Info")
print("Downloader: Firmware Build " + data['firmwares'][int(firmwareid) - 1]['buildid'])
print("Downloader:          md5hash " + md5sum)
print("Downloader: Start downloading")
r = requests.get(downloadlink, stream=True)

#with open(os.path.basename(downloadlink), 'wb') as f:
#    file_size = int(r.headers["content-length"])
#    chunk_size = 1000
#    with tqdm(ncols=100, desc="Downloader: Fetching " + os.path.basename(downloadlink), total=file_size, unit_scale=True) as pbar:
#        # 1k for chunk_size, since Ethernet packet size is around 1500 bytes
#        for chunk in r.iter_content(chunk_size=chunk_size):
#            f.write(chunk)
#            pbar.update(chunk_size)
print("Downloader: Download complete")
print("iOSUtils: Initializing JAVA environment.")
jvm_path = jpype.getDefaultJVMPath()
print("iOSUtils: JVM Path: " + jvm_path)
if not jpype.isJVMStarted():
    jpype.startJVM(jvm_path, "-ea", "-Djava.class.path=%s" % "iOSUtils.jar")
Utils = jpype.JClass("Utils.Utils")
KeyTypes = jpype.JClass("KeyTypes")
utils_class = Utils()
keytypes_class = KeyTypes()
utils_class.getKeyFor("iPad3,1", "8.4.1", keytypes_class.KERNELCACHE).getKey()