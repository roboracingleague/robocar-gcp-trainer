#!/bin/bash

# This script upload a given archive to GCS
if [[ -z "${STEERING_BUCKET_NAME}" ]]; then
    echo "Missing STEERING_BUCKET_NAME env variable"
    exit
fi
src="gs://${STEERING_BUCKET_NAME}/models"
if [[ -z "$1" ]]; then
    echo "usage : $0 <model>"
    echo "example : $0 pilot-data-2023_01_25.tar.tflite"
    exit
fi
gsutil cp $src/$1 .

echo "File ${src}/$1 has been downloaded here"