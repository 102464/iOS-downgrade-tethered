import os
import osinfo


def patch_iBoot(osInfo: osinfo.OSInfo, path, filename, bootargs=""):
    if bootargs == "":
        args = ""
    else:
        args = "-b \"" + bootargs + "\""
    os.system("cd " + os.path.abspath(".") + "; " +
              "./tool/" + osInfo.getosplatform() + "/iBoot32Patcher " + path + " " + filename +
              " " + args)
