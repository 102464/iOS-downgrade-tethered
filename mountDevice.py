import os

import osinfo


def mountDevice(osInfo: osinfo.OSInfo, dmgImagePath, mountpoint):
    if osInfo.getosplatform() == "macosx":
        os.system("cd " + os.path.abspath("./DeviceSupport/iPad3_1") + "; " +
                  "hdiutil attach " + dmgImagePath + " -mountpoint " + mountpoint)
    if osInfo.getosplatform() == "linux":
        # TODO: Add code for mounting dmg file on linux.
        pass
    if osInfo.getosplatform() == "windows":
        # TODO: Add code for extracting (not mounting) dmg file on Windows.
        pass


def unmountDevice(osInfo: osinfo.OSInfo, mountpoint):
    if osInfo.getosplatform() == "macosx":
        os.system("cd " + os.path.abspath("./DeviceSupport/iPad3_1") + "; " +
                  "hdiutil detach " + mountpoint)
    if osInfo.getosplatform() == "linux":
        # TODO: Add code for unmounting dmg file on linux.
        pass
    if osInfo.getosplatform() == "windows":
        # TODO: Add code for deleting (not unmounting) extracted content on Windows.
        pass
