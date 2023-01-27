#!/bin/bash

# This script upload a given archive to GCS
if [[ -z "${STEERING_BUCKET_NAME}" ]]; then
    echo "Missing STEERING_BUCKET_NAME env variable"
    exit
fi
dest="gs://${STEERING_BUCKET_NAME}/training/"
if [[ -z "$1" ]]; then
    echo "usage : $0 <archive>"
    echo "example : $0 data-2023_01_25.tar.gz"
    exit
fi
gsutil cp $1  $dest

echo "File $1 has been uploaded to ${dest}"