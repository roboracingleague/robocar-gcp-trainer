#!/bin/bash

if [[ -z "$1" ]]; then
    echo "usage : $0 <archive> <model>"
    echo "example : $0 data-2023_01_25.tar.gz mymodel.h5"
    exit
fi

if [[ -z "$2" ]]; then
    echo "usage : $0 <archive> <model>"
    echo "example : $0 data-2023_01_25.tar.gz mymodel.h5"
    exit
fi


jobname="steering$(date +"%Y%m%d%H%M")"

outfile="$(basename $2 .h5).mp4"

gcloud ai-platform jobs submit training "$jobname" \
  --package-path task \
  --module-name task.makemovie \
  --scale-tier BASIC_GPU \
  --region $REGION --python-version 3.7 --runtime-version 2.9 --job-dir $JOB_DIR --stream-logs -- --out ${outfile} --bucket ${STEERING_BUCKET_NAME} --archive $1 --type linear --model $2 --salient

#  --packages ~/projects/rrl_2023/donkeycar/donkeycar.tar.gz \

