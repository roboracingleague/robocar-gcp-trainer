#!/bin/bash

# this script package all data found in given tub directory and complete it with donkeycar config files

if [[ -z "$1" ]]; then
    echo "Missing explicit tub directory !"
    echo "Usage : $0  <tub directory> <archive name>"
    exit
else
    TUB_DIR=$1
fi

if [[ -z "$2" ]]; then
    echo "Missing archive name !"
    echo "Usage : $0  <tub directory> <archive name>"
    exit
else
    base_filename="$2"
fi

if [ ! -f ./config.py ]
then
	echo "Could not find ./config.py !"
    echo "You must call this script from a 'mycar' directory"
    exit
fi

if [ ! -f ./myconfig.py ]
then
	echo "Could not find ./myconfig.py !"
    echo "You must call this script from a 'mycar' directory"
    exit
fi


echo "Archiving ${TUB_DIR} to $base_filename.tgz"
tar -chf $base_filename.tar -C ./${TUB_DIR} . 
touch myconfig.py config.py
tar -uhf $base_filename.tar myconfig.py config.py
gzip $base_filename.tar
mv $base_filename.tar.gz $base_filename.tgz 

echo "File ${base_filename}.tgz created"

