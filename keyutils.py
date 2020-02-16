import argparse
import json
import ioscrypto

from urllib.request import urlopen

parser = argparse.ArgumentParser()
parser.add_argument("--mode", help="Set mode of getting keys."
                    "Available options are localKey networkKey and downloadKeys")
parser.add_argument("--location", help="Set location to download from (github/gitee). "
                    "specify it when using localKey. ")
parser.add_argument("--deviceId", help="Specify a device id for downloading keys. "
                    "use it when using downloadKeys")
args = parser.parse_args()

try:
    print("Welcome to KeyUtils in iOS-downgrade-tethered.")
    print("Mode args: " + args.mode)
    if args.mode == "localKey":
        chosen = False
        if args.location == "github":
            chosen = True
        if args.location == "gitee":
            chosen = True
            print("Downloading keys from gitee")
        if not chosen:
            print("Location is invalid. Exiting.")
            exit(255)
    if args.mode == "networkKey":
        print("Not supported yet.")
        # TODO: Write some code here
    if args.mode == "downloadKeys":
        print("Starting download keys for device " + args.deviceId)
        try:
            apiurl = "http://api.ipsw.me/v4"
            f = urlopen(apiurl + "/device/" + args.deviceId + "?type=ipsw")
            with open("firmware-api.json", "wb") as code:
                code.write(f.read())
            data = json.load(open("firmware-api.json"))
            num = len(data['firmwares'])
            kdict = {}
            firmwares = {}
            for i in range(0, num - 1):
                keys = {}
                ivs = {}
                keysAndivs = {}
                keys, ivs = ioscrypto.getKeyAndIV(data['firmwares'][i]['version'], args.deviceId)
                keysAndivs = {"keys": keys, "ivs": ivs}
                firmwares.update({data['firmwares'][i]['version']: keysAndivs})
            kdict.update({args.deviceId: firmwares})
            dat = json.dumps(kdict)
            fd = open("firmware-keys.json", mode="w", encoding="utf-8")
            fd.write(dat)
            fd.close()
            print("Keys have been saved to firmware-keys.json.")
        except Exception as ex:
            print("Exception occurred. Device ID may be not exist!")

except TypeError as ex:
    print("Invalid argument.")
    exit(255)
