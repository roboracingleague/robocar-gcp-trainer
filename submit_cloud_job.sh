#!/bin/bash

if [[ -z "$1" ]]; then
    echo "usage : $0 <archive>"
    echo "example : $0 data-2023_01_25.tar.gz"
    exit
fi

jobname="steering$(date +"%Y%m%d%H%M")"

gcloud ai-platform jobs submit training "$jobname" \
  --package-path trainer \
  --module-name trainer.task \
  --scale-tier BASIC_GPU \
  --region $REGION --python-version 3.7 --runtime-version 2.9 --job-dir $JOB_DIR --stream-logs -- --archive $1

#  --packages ~/projects/rrl_2023/donkeycar/donkeycar.tar.gz \

