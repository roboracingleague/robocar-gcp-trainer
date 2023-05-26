#!/bin/bash

Help()
{
   # Display Help
   echo "Download models from GCS."
   echo "Source GCS bucket is defined by STEERING_BUCKET_NAME env variable"
   echo
   echo "Syntax: $0 [-m <model basename>] [-h]"
   echo "options:"
   echo "m     specify model basename (without extension, default to 'pilot-wip')."
   echo "h     Print this Help."
   echo
}

model=""

while getopts ":hm:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      m) # Enter a name
         model=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         Help
         exit;;
   esac
done

if [[ -z "$model" ]]; then
    model="pilot-wip"
    echo "using default model basename $model"
fi

# This script upload a given archive to GCS
if [[ -z "${STEERING_BUCKET_NAME}" ]]; then
    echo "Missing STEERING_BUCKET_NAME env variable"
    exit
fi
src="gs://${STEERING_BUCKET_NAME}/models"

gsutil cp $src/$model.h5 .
gsutil cp $src/$model.tflite .
gsutil cp $src/$model.onnx .

echo "Files ${src}/$model.[h5|tflite|onnx] has been downloaded in current directory"