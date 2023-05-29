#!/bin/bash

Help()
{
   # Display Help
   echo "Perform training task locally."
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

if [[ -z "$TRAINER_DIR" ]]; then
    echo "Missing env variable TRAINER_DIR !"
    exit
fi

if [[ -z "$JOB_DIR" ]]; then
    echo "Missing env variable JOB_DIR !"
    exit
fi

if [[ -z "$STEERING_BUCKET_NAME" ]]; then
    echo "Missing env variable STEERING_BUCKET_NAME !"
    exit
fi

if [[ -z "$archive" ]]; then
    archive="wip.tgz"
    echo "using default archive name $archive"
fi

dest="gs://${STEERING_BUCKET_NAME}/training/"

gcloud ai-platform local train \
  --package-path $TRAINER_DIR/task \
  --module-name task.train \
  --job-dir $JOB_DIR -- --bucket ${STEERING_BUCKET_NAME} --archive $archive --model scene_detector

#  --packages ~/projects/rrl_2023/donkeycar/donkeycar.tar.gz \
