## Disclaimer
This is BETA software. This may boot loop or brick your device if you don't know what you're doing. 

# iOS-downgrade-tethered

### Description
**Downgrade method from** [here](https://www.reddit.com/r/jailbreak/comments/7v6pxu/release_tutorial_how_to_downgrade_any_32_bit) <br />

A simple downgrade script which can downgrade 32-bit devices to ANY version. <br />

Currently supported device is iPad3,1. Supported iOS is iOS 7-9.1. More will add in the future. <br />

***IMPORTANT***: This tool does not use any BootROM exploits. <br />
Do not power off your device if you have downgraded your device using this tool. It will **BRICK** your device. <br />
The only way to power off is: jailbreak your device, then run `./kloader pwnediBSS` in your shell. <br />

If your device is supported by checkm8 exploitation tool (such as [ipwndfu](https://github.com/axi0mX/ipwndfu)), maybe you can still boot even you have powered off your device. <br />
see also: [https://github.com/Benfxmth/a5-a6-tethered-ios-downgrade-bash-scripts](https://github.com/Benfxmth/a5-a6-tethered-ios-downgrade-bash-scripts) <br />

### Usage

Install requirements: `pip3 install -r requirements.txt` (Only supports python3)<br />
Run `./downgrade.py` and follow the on-screen instructions.

### Problems and Solutions

+ javax.net.ssl.SSLHandshakeException: sun.security.validator.ValidatorException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target <br />
Solution: Run `javac InstallCert.java; java InstallCert theiphonewiki.com:80 changeit` and retry.

### TODO

Future plans: 
+ Jailbreak support 
+ Add support for iPhone 4S (iPhone4,1)

### Credits

@planetbeing for dmg [https://github.com/planetbeing/xpwn](https://github.com/planetbeing/xpwn) <br />
@westbaer for irecovery [https://github.com/westbaer/irecovery](https://github.com/westbaer/irecovery) <br />
@nyansatan for dualbootstuff [https://github.com/nyansatan/nyansatan.github.io](https://github.com/nyansatan/nyansatan.github.io) <br />
@Benfxmth for downgrade method and script [https://github.com/Benfxmth/a5-a6-tethered-ios-downgrade-bash-scripts](https://github.com/Benfxmth/a5-a6-tethered-ios-downgrade-bash-scripts) <br />
@iH8Sn0w for iBoot32Patcher [https://github.com/iH8sn0w/iBoot32Patcher](https://github.com/iH8sn0w/iBoot32Patcher) <br />
@JonathanSeals for CoolBooter [https://coolbooter.com](https://coolbooter.com) <br />
@winocm for kloader [https://twitter.com/winocm](https://twitter.com/winocm)
## Although this project is completed, it has not been tested, so maybe it has some ***CRITICAL*** bugs. so this is for testing purposes only. Do not use it on your device.
