#!/bin/bash


Help()
{
   # Display Help
   echo "Perform makemovie task locally."
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

outfile="$(basename $model .h5).mp4"

if [[ -z "${STEERING_BUCKET_NAME}" ]]; then
    echo "Missing STEERING_BUCKET_NAME env variable"
    exit
fi

src="gs://${STEERING_BUCKET_NAME}/training/"

gcloud ai-platform local train \
  --package-path $TRAINER_DIR/task \
  --module-name task.makemovie \
  --job-dir $JOB_DIR -- --out ${outfile} --bucket ${STEERING_BUCKET_NAME} --archive $archive --type linear --model $model --salient

#  --packages ~/projects/rrl_2023/donkeycar/donkeycar.tar.gz \
