import os

import osinfo


def waitForConnection(osInfo: osinfo.OSInfo):
    print("Waiting for DFU/Recovery connection. Please unplug and replug your device.")
    while True:
        res = os.system("./tools/" + osInfo.getosplatform() + "/irecovery -c /exit")
        if res:
            break
    print("Device has successfully connected.")


def send_iBEC(osInfo: osinfo.OSInfo, path):
    print("Sending iBEC.")
    x = 1
    while True:
        res = os.system("./tools/" + osInfo.getosplatform() + "/irecovery -f " + path)
        if res:
            break
        print("Failed to send iBEC! Retrying....")
        if x == 5:
            print("Retrying for 5 times but still failed. exiting.")
            exit(1)
        x = x + 1
        print("Successfully sent iBEC.")


def tether_boot_up_device(osInfo: osinfo.OSInfo):
    print("Trying to tether boot up device.")
    print("Sending DeviceTree")
    os.system("./tools/" + osInfo.getosplatform() + "/irecovery -c /send DeviceTree")
    print("Executing DeviceTree")
    os.system("./tools/" + osInfo.getosplatform() + "/irecovery -c devicetree")
    print("Sending kernelcache")
    os.system("./tools/" + osInfo.getosplatform() + "/irecovery -c /send kernelcache")
    print("Booting your device")
    os.system("./tools/" + osInfo.getosplatform() + "/irecovery -c bootx")