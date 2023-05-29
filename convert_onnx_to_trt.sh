#!/bin/bash

Help()
{
   # Display Help
   echo "Convert mode from ONNX to TRT."
   echo "Must be invoked on a NVIDIA equipped host running JetPack"
   echo
   echo "Syntax: $0 [-i <onnx model file>] [-h]"
   echo "options:"
   echo "i     specify model file path, mandatory"
   echo "h     Print this Help."
   echo
}

filename=""

while getopts ":hi:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      i) # Enter a name
         finelame=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         Help
         exit;;
   esac
done

if [[ -z "$DONKEYCAR_DIR" ]]; then
    echo "Missing env variable DONKEYCAR_DIR !"
    exit
fi

if [[ -z "$filename" ]]; then
    echo "Missing filename, exit"
    exit
fi

output = "${filename%.onnx}.trt"
echo "Convert $filename to $output"
python $DONKEYCAR_DIR/donkeycar/tools/tensorrt/build_save_trt_engine.py --onnx $filename --savedtrt $output
