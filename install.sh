#!/bin/bash

if [[ -z "$TRAINER_DIR" ]]; then
    echo "Missing env variable TRAINER_DIR !"
    exit
fi
declare -a ScriptsArray=("convert_onnx_to_trt.sh" "make_tub_archive.sh" "deflate_tub_archive.sh" "upload_tub_archive.sh" "local_train.sh" "local_train_scene.sh" "local_makemovie.sh" "submit_cloud_train.sh" "submit_cloud_train_scene.sh" "submit_cloud_makeusermovie.sh" "submit_cloud_makepilotmovie.sh" "download_model.sh" "download_tub_archive.sh" )

for script in ${ScriptsArray[@]}; do

    if [[ -f "$TRAINER_DIR/$script" ]]; then
        echo "Install script $script"
        ln -f -s $TRAINER_DIR/$script .
    fi

 done