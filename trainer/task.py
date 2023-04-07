# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Trains a Keras model to predict income bracket from other Census data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from . import util

import argparse
import os
from pathlib import Path

import tensorflow as tf

from donkeycar.parts.tub_v2 import Tub
from donkeycar.pipeline.training import train
from donkeycar.pipeline.database import PilotDatabase
import donkeycar as dk

def get_args():
    """Argument parser.

    Returns:
      Dictionary of arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--job-dir',
        type=str,
        required=True,
        help='local or GCS location for writing checkpoints and exporting '
             'models')
    parser.add_argument(
        '--archive',
        type=str,
        required=True,
        help='config file')
    parser.add_argument(
        '--bucket',
        type=str,
        required=True,
        help='bucket name to use')
    parser.add_argument(
        '--verbosity',
        choices=['DEBUG', 'ERROR', 'FATAL', 'INFO', 'WARN'],
        default='INFO')

    args, _ = parser.parse_known_args()
    return args


class DonkeyTrainer:

    def __init__(self) -> None:
        self.tmpdir = "."

    def get_archive(self):
        self.tmpdir = util.get_archive(bucket_name=args.bucket, url=args.archive)

    def get_config(self):
        self.cfg = dk.load_config(config_path=os.path.join(self.tmpdir, "config.py"))
        self.tub_path = self.tmpdir

    def train_and_evaluate(self, args):

        self.tub_path  = self.tmpdir
        modelfilepath=os.path.join(self.tmpdir, self.cfg.MODELS_PATH)
        os.makedirs(modelfilepath, exist_ok=True)

        history = train(self.cfg, tub_paths=self.tub_path,
                        model_type=self.cfg.DEFAULT_MODEL_TYPE,
                        transfer=None,
                        comment="")

    def save_model(self, ext, bucket, output_name):
        database = PilotDatabase(self.cfg)
        filename = f"{database.entries[0]['Name']}.{ext}"
        filepath=os.path.join(self.tmpdir, self.cfg.MODELS_PATH)
        util.save_model(bucket, filepath, src_filename=filename, dst_filename=output_name)
        print(f"Model {filepath}/{filename} exported to bucket {bucket} as {output_name}")

if __name__ == '__main__':
    args = get_args()
    tf.compat.v1.logging.set_verbosity(args.verbosity)
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    trainer = DonkeyTrainer()
    print(f"Download data set archive {args.archive}")
    trainer.get_archive()
    print(f"Getting config files from archive")
    trainer.get_config()
    print (f"TF FLite creation : {trainer.cfg.CREATE_TF_LITE}")
    print (f"ONNX creation : {trainer.cfg.CREATE_ONNX_MODEL}")
    print(f"Training model")
    trainer.train_and_evaluate (args)

    h5_modelname = f"pilot-{Path(args.archive).stem}.h5"
    print(f"Exporting h5 model")
    trainer.save_model(ext='h5', bucket=args.bucket, output_name=h5_modelname)

    if trainer.cfg.CREATE_TF_LITE:
        tflite_modelname = f"pilot-{Path(args.archive).stem}.tflite"
        print(f"Exporting tflite model")
        trainer.save_model (ext='tflite', bucket=args.bucket, output_name=tflite_modelname)
    if trainer.cfg.CREATE_ONNX_MODEL:
        onnx_modelname = f"pilot-{Path(args.archive).stem}.onnx"
        print(f"Exporting onnx model")
        trainer.save_model (ext='onnx', bucket=args.bucket, output_name=onnx_modelname)
