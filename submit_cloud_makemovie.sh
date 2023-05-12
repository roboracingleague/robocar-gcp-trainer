#!/bin/bash

Help()
{
   # Display Help
   echo "Submit makemovie task to GCP AI Platform."
   echo
   echo "Syntax: $0 [-m <model.h5>] [-a <archive name>] [-h]"
   echo "options:"
   echo "m     model filename (expecting .h5)."
   echo "a     archive filename to use (including extension, default to 'wip.tgz')."
   echo "h     Print this Help."
   echo
}

model=""
archive=""

while getopts ":hm:a:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      m) # Enter a name
         model=$OPTARG;;
      a) # Enter a name
         archive=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         Help
         exit;;
   esac
done

if [[ -z "$model" ]]; then
    model="pilot-wip.h5"
    echo "Using default model filename '$tub'"
fi

if [[ -z "$archive" ]]; then
    archive="wip.tgz"
    echo "using default archive name $archive"
fi


jobname="steering$(date +"%Y%m%d%H%M")"

outfile="$(basename $2 .h5).mp4"

gcloud ai-platform jobs submit training "$jobname" \
  --package-path task \
  --module-name task.makemovie \
  --scale-tier BASIC_GPU \
  --region $REGION --python-version 3.7 --runtime-version 2.9 --job-dir $JOB_DIR --stream-logs -- --out ${outfile} --bucket ${STEERING_BUCKET_NAME} --archive $archive --type linear --model $1 --salient

#  --packages ~/projects/rrl_2023/donkeycar/donkeycar.tar.gz \

