import os
import osinfo

from jpype import *


def getKeyAndIV(firmwareversion, deviceidentifier):
    jvm_path = getDefaultJVMPath()
    print("iOSUtils: JVM Path: " + jvm_path)
    if not isJVMStarted():
        startJVM(jvm_path, "-ea", "-Djava.class.path=" + os.path.join(os.path.abspath(""), "iOSUtils-jdk7.jar"))
    java.lang.System.out.println("If you see this message, that means JVM works well.")
    print("iOSUtils: importing CA certificate")
    java.lang.System.setProperty("javax.net.ssl.trustStore", "cacerts")
    # Set keystore password
    java.lang.System.setProperty("javax.net.ssl.trustStorePassword", "changeit")
    # Set proxy settings (Chinese users may need that)
    # Comment this if you don't need proxy to access the Internet
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
    print("iOSUtils: Getting RestoreRamdisk key for version " + firmwareversion + ", device " + deviceidentifier)
    restoreramdisk_key = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.RESTORE_RD).getKey()
    print("iOSUtils: Getting kernelcache key for version " + firmwareversion + ", device " + deviceidentifier)
    kernelcache_key = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.KERNELCACHE).getKey()
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
    print("iOSUtils: Getting RestoreRamdisk IV for version " + firmwareversion + ", device " + deviceidentifier)
    restoreramdisk_iv = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.RESTORE_RD).getIv()
    print("iOSUtils: Getting kernelcache IV for version " + firmwareversion + ", device " + deviceidentifier)
    kernelcache_iv = utils_class.getKeyFor(deviceidentifier, firmwareversion, KeyTypes.KERNELCACHE).getIv()
    print("          iBSS Key: " + ibss_key)
    print("                IV: " + ibss_iv)
    print("          iBEC Key: " + ibec_key)
    print("                IV: " + ibec_iv)
    print("     AppleLogo Key: " + applelogo_key)
    print("                IV: " + applelogo_iv)
    print("    DeviceTree Key: " + devicetree_key)
    print("                IV: " + devicetree_iv)
    print("RestoreRamdisk Key: " + restoreramdisk_key)
    print("                IV: " + restoreramdisk_iv)
    print("   KernelCache Key: " + kernelcache_key)
    print("                IV: " + kernelcache_iv)
    print("        RootFS Key: " + rootfs_key)
    keydict = {"ibss": ibss_key, "ibec": ibec_key, "applelogo": applelogo_key,
               "devicetree": devicetree_key, "restoreRamdisk": restoreramdisk_key,
               "kernelcache": kernelcache_key, "rootfs": rootfs_key}
    ivdict = {"ibss": ibec_iv, "ibec": ibec_iv, "applelogo": applelogo_iv,
              "devicetree": devicetree_iv, "restoreRamdisk": restoreramdisk_iv,
              "kernelcache": kernelcache_iv}
    return keydict, ivdict


def decryptImg3(osInfo: osinfo.OSInfo, path, destination, key, iv, decryptFlag: bool = False):
    if decryptFlag:
        flag = "-decrypt"
    else:
        flag = ""
    os.system("cd " + os.path.abspath("") + "; " +
              "./tool/" + osInfo.getosplatform() + "/xpwntool " + path + " " +
              destination + " " + " -k " + key +
              " -iv " + iv + " " + flag)


def decryptRootFS(osInfo: osinfo.OSInfo, path, key):
    newfile = os.path.basename(path).split(".")[0] + ".decrypted.dmg"
    os.system("cd " + os.path.abspath(".") + "; " +
              "./tool/" + osInfo.getosplatform() + "/dmg extract " + path + " " +
              newfile + " -k " + key)
    if osInfo.getosplatform() == "macosx":
        print("hdiutil: converting format")
        os.system("cd " + os.path.abspath(".") + "; " +
                  "hdiutil convert -format UDZO -o RootFilesystem.dmg " + newfile)
        print("ASR: Scanning image")
        ret = os.system("cd " + os.path.abspath(".") + "; " +
                        "asr -imagescan RootFilesystem.dmg")
        if ret > 0:
            print("ERROR: Image scan did not passed.")
            print("exiting")
            exit(ret)
    if osInfo.getosplatform() == "linux" or osInfo.getosplatform() == "windows":
        print("dmg: converting image")
        os.system("cd " + os.path.abspath(".") + "; " +
                  "./tool/" + osInfo.getosplatform() + "/dmg build " + newfile + " " + os.path.basename(path))
        print("WARNING: on linux or windows there will not be an image scan.")
        print("         please make sure image is not corrupted.            ")
