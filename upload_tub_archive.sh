#!/bin/bash

Help()
{
   # Display Help
   echo "Upload archive to GCS."
   echo "Target GCS bucket is defined by STEERING_BUCKET_NAME env variable"
   echo
   echo "Syntax: $0 [-a <archive name>] [-h]"
   echo "options:"
   echo "a     specify local archive name (with extension, default to 'wip.tgz')."
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

if [[ ! -f "$archive" ]]; then
    echo "Archive file $archive not found"
    exit
fi

# This script upload a given archive to GCS
if [[ -z "${STEERING_BUCKET_NAME}" ]]; then
    echo "Missing STEERING_BUCKET_NAME env variable"
    exit
fi
dest="gs://${STEERING_BUCKET_NAME}/training/"

gsutil cp $archive  $dest

echo "File $archive has been uploaded to ${dest}"