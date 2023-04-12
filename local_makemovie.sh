#!/bin/bash

# This script upload a given archive to GCS
if [[ -z "${JOB_DIR}" ]]; then
    echo "Missing JOB_DIR env variable"
    exit
fi
dest="gs://${STEERING_BUCKET_NAME}/training/"
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

outfile="$(basename $2 .h5).mp4"

gcloud ai-platform local train \
  --package-path task \
  --module-name task.makemovie \
  --job-dir $JOB_DIR -- --out ${outfile} --bucket ${STEERING_BUCKET_NAME} --archive $1 --type linear --model $2 --salient

#  --packages ~/projects/rrl_2023/donkeycar/donkeycar.tar.gz \
