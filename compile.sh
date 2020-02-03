#!/bin/sh
cd ../iOSUtils/src/iOSUtils
javac KeyTypes.java DeviceComponent.java Utils.java
jar -cvf iOSUtils.jar KeyTypes.class DeviceComponent.class Utils.class
cp iOSUtils.jar ../../../iOS-downgrade-tethered/
cd ../../../iOS-downgrade-tethered
