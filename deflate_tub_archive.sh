#!/bin/bash

Help()
{
   # Display Help
   echo "Deflate archive to tub directory and restore config in current directory."
   echo "Warning : tub directory will be cleaned before"
   echo
   echo "Syntax: $0 [-a <archive name>] [-t <tub directory>] [-h]"
   echo "options:"
   echo "t     specify tub directory where to deflate archive (default to 'data')."
   echo "a     specify source archive filename (including extension, default to 'wip.tgz')."
   echo "h     Print this Help."
   echo
}

tub=""
filename=""

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

if [[ -z "$filename" ]]; then
    filename="wip.tgz"
    echo "using default archive name $archive"
fi

echo "Cleaning ${tub}"
rm -r -f ${tub}
mkdir ${tub}

echo "Deflating $filename to ${tub}"
tar -xzf ${filename} -C ${tub}

if [ -f ${tub}/myconfig.py ]
then
    echo "Restoring myconfig.py from archive"
    cp ${tub}/myconfig.py .
fi

if [ -f ${tub}/config.py ]
then
    echo "Restoring config.py from archive"
    cp ${tub}/config.py .
fi

echo "File ${filename} deflated"

