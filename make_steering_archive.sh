#!/bin/bash

# this script package all data found in given tub directory and complete it with donkeycar config files
filename="data-$(date +"%Y_%m_%d").tar"

if [[ -z "$1" ]]; then
    TUB_DIR="data"
    echo "Missing explicit tub directory, using default ${TUB_DIR}"
else
    TUB_DIR=$1
fi

echo "Archiving ${TUB_DIR}"
echo $filename
tar -chf $filename -C ./${TUB_DIR} . 
tar -uhf $filename myconfig.py config.py
gzip $filename

echo "File ${filename} created"

