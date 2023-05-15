#!/bin/bash

Help()
{
   # Display Help
   echo "Download dataset archive from GCS."
   echo "Source GCS bucket is defined by STEERING_BUCKET_NAME env variable"
   echo
   echo "Syntax: $0 [-a <archive name>] [-h]"
   echo "options:"
   echo "a     specify source archive name to download (including extension, default to 'wip.tgz')."
   echo "h     Print this Help."
   echo
}

archive=""

while getopts ":ha:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      a) # Enter a name
         archive=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         Help
         exit;;
   esac
done

if [[ -z "$archive" ]]; then
    archive="wip.tgz"
    echo "using default archive name $archive"
fi

if [[ -z "${STEERING_BUCKET_NAME}" ]]; then
    echo "Missing STEERING_BUCKET_NAME env variable"
    exit
fi

src="gs://${STEERING_BUCKET_NAME}/training"

gsutil cp $src/$archive .

echo "File $src/$archive has been downloaded in current directory"