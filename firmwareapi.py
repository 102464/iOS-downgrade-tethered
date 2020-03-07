import os

from urllib.request import urlopen


def getfirmwarejson(deviceidentifier):
    print("API: Downloading device information.")
    if not os.path.exists("firmware-api.json"):
        apiurl = "http://api.ipsw.me/v4"
        f = urlopen(apiurl + "/device/" + deviceidentifier + "?type=ipsw")
        with open("firmware-api.json", "wb") as code:
            code.write(f.read())
    else:
        print("API: file \"firmware-api.json\" already exists. Please remove for update.")
