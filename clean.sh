#!/bin/sh
echo "Cleaning up"
rm -rf *.img3 pwned* *.dfu *.dmg nohup.out
mv firmware iPad3,1_8.0_12A365_Restore.ipsw ../
echo "Success"
