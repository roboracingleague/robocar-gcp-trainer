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

if [[ -z "$model" ]]; then
    model="pilot-wip.h5"
    echo "Using default model filename '$tub'"
fi

if [[ -z "$archive" ]]; then
    archive="wip.tgz"
    echo "using default archive name $archive"
fi

jobname="salient_$(date +"%Y%m%d%H%M")"
if [[ ! -z "$JOB_PREFIX" ]]; then
    jobname="$(JOB_PREFIX)_$(jobname)"
fi


outfile="$(basename $model .h5)-salient.mp4"

gcloud ai-platform jobs submit training "$jobname" \
  --package-path $TRAINER_DIR/task \
  --module-name task.makemovie \
  --scale-tier BASIC_GPU \
  --region $REGION --python-version 3.7 --runtime-version 2.9 --job-dir $JOB_DIR --stream-logs -- --out ${outfile} --bucket ${STEERING_BUCKET_NAME} --archive $archive --type linear --model ${model} --salient

src="gs://${STEERING_BUCKET_NAME}/models"

gsutil cp ${src}/movies/${outfile} .
