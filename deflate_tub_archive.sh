#!/bin/bash

# this script package all data found in given tub directory and complete it with donkeycar config files

if [[ -z "$1" ]]; then
    echo "Missing archive name !"
    echo "Usage : $0 <archive name>  <tub directory>"
    exit
else
    filename=$1
fi

if [[ -z "$2" ]]; then
    echo "Missing explicit tub directory !"
    echo "Usage : $0  <archive name> <tub directory> "
    exit
else
    TUB_DIR=$2
fi

echo "Cleaning ${TUB_DIR}"
rm -r -f ${TUB_DIR}
mkdir ${TUB_DIR}

echo "Deflating $filename to ${TUB_DIR}"
tar -xzf ${filename} -C ${TUB_DIR}

if [ ! -f ${TUB_DIR}/myconfig.py ] then
    echo "Restoring myconfig.py from archive"
    cp ${TUB_DIR}/myconfig.py .
fi

if [ ! -f ${TUB_DIR}/config.py ] then
    echo "Restoring config.py from archive"
    cp ${TUB_DIR}/config.py .
fi

echo "File ${filename} deflated"

