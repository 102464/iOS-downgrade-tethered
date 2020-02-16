import argparse
import json

import ioscrypto

parser = argparse.ArgumentParser()
parser.add_argument("--mode", help="Set mode of getting keys. Available options are localKey and networkKey")
parser.add_argument("--location", help="Set location to download from. (github/gitee)")
args = parser.parse_args()

try:
    print("Welcome to KeyUtils in iOS-downgrade-tethered.")
    print("Mode args: " + args.mode)
    if args.mode == "localKey":
        chosen = False
        if args.location == "github":
            chosen = True
            print("Downloading keys from github")
            data = json.load(open("firmware-api.json"))
            num = len(data['firmwares'])
            kdict = {}
            firmwares = {}
            #kdict.update("iPad3,1")
            for i in range(0, num - 1):
                keys = {}
                ivs = {}
                keysAndivs = {}
                keys, ivs = ioscrypto.getKeyAndIV(data['firmwares'][i]['version'], 'iPad3,1')
                keysAndivs = {"keys": keys, "ivs": ivs}
                firmwares.update({data['firmwares'][i]['version']: keysAndivs})
            kdict.update({"iPad3,1": firmwares})
            dat = json.dumps(kdict)
            fd = open("firmware-keys.json", mode="w", encoding="utf-8")
            fd.write(dat)
            fd.close()
        if args.location == "gitee":
            chosen = True
            print("Downloading keys from gitee")
        if not chosen:
            print("Location is invalid. Exiting.")
            exit(255)
except TypeError as ex:
    print("Invalid argument.")
    exit(255)
