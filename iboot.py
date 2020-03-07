import os
import osinfo


def patch_iBoot(osInfo: osinfo.OSInfo, path, filename, bootargs=""):
    if bootargs == "":
        args = ""
    else:
        args = "-b \"" + bootargs + "\""
    os.system("cd " + os.path.abspath(".") + "; " +
              "./tools/" + osInfo.getosplatform() + "/iBoot32Patcher " + path + " " + filename +
              " " + args)


def fix_iBSS():
    # Why iBSS always corrupted after decrypting in python os.system() function,
    # but decrypting using command line is OK???

    # Corrupted header: bd 99 d0 cb a7 dc cd e7 19 65 07 38 81 2b bc c6
    #    Normal header: 0e 00 00 ea 18 f0 9f e5 18 f0 9f e5 18 f0 9f e5
    print("Fixing iBSS.")
    ibss_normal_header = b'\x0e\x00\x00\xea\x18\xf0\x9f\xe5\x18\xf0\x9f\xe5\x18\xf0\x9f\xe5'
    ibss = open("iBSS", "r+b")
    ibss.write(ibss_normal_header)
    ibss.close()
    print("DONE")
