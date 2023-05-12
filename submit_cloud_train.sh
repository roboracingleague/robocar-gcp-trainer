#!/bin/bash

Help()
{
   # Display Help
   echo "Submit training task to GCP AI Platform."
   echo
   echo "Syntax: $0 [-a <archive name>] [-h]"
   echo "options:"
   echo "a     specify target archive name (including extension, default to 'wip.tgz')."
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

jobname="steering$(date +"%Y%m%d%H%M")"

gcloud ai-platform jobs submit training "$jobname" \
  --package-path task \
  --module-name task.train \
  --scale-tier BASIC_GPU \
  --region $REGION --python-version 3.7 --runtime-version 2.9 --job-dir $JOB_DIR --stream-logs -- --bucket $STEERING_BUCKET_NAME --archive $archive

#  --packages ~/projects/rrl_2023/donkeycar/donkeycar.tar.gz \

