#!/bin/bash

# This script upload a given archive to GCS
if [[ -z "${JOB_DIR}" ]]; then
    echo "Missing JOB_DIR env variable"
    exit
fi
dest="gs://${STEERING_BUCKET_NAME}/training/"
if [[ -z "$1" ]]; then
    echo "usage : $0 <archive>"
    echo "example : $0 data-2023_01_25.tar.gz"
    exit
fi

gcloud ai-platform local train \
  --package-path trainer \
  --module-name trainer.task \
  --job-dir $JOB_DIR -- --bucket ${STEERING_BUCKET_NAME} --archive $1

#  --packages ~/projects/rrl_2023/donkeycar/donkeycar.tar.gz \
