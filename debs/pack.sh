#!/bin/sh
echo "Packing \"Packages.bz2\""
cp Packages Packages.bak
rm Packages.bz2
bzip2 Packages
mv Packages.bak Packages
echo "DONE"
