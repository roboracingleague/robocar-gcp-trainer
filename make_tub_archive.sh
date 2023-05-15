#!/bin/bash

Help()
{
   # Display Help
   echo "Make archive of tub directory, including current config files."
   echo
   echo "Syntax: $0 [-t <tub directory>] [-a <archive basename>] [-h]"
   echo "options:"
   echo "t     specify tub directory to archive (default to 'data')."
   echo "a     specify target archive basename (without extension, default to 'wip')."
   echo "h     Print this Help."
   echo
}

tub=""
archive=""

while getopts ":ht:a:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      t) # Enter a name
         tub=$OPTARG;;
      a) # Enter a name
         archive=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         Help
         exit;;
   esac
done

if [[ -z "$tub" ]]; then
    tub="data"
    echo "Using default tub directory '$tub'"
fi

if [[ ! -d "$tub" ]]; then
    echo "tub directory '$tub' not found"
    exit
fi

if [[ -z "$archive" ]]; then
    archive="wip"
    echo "using default archive basename $archive"
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

echo "Archiving ${tub} to $archive.tgz"
tar -chf $archive.tar -C ./${tub} . 
touch myconfig.py config.py
tar -uhf $archive.tar myconfig.py config.py
gzip $archive.tar
mv $archive.tar.gz $archive.tgz 

echo "File ${archive}.tgz created"