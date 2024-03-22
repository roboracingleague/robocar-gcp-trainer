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

import sys
import argparse
import os
from pathlib import Path
import traceback
import tempfile
import datetime
import glob

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
        required=True,
        help='local or GCS location for writing checkpoints and exporting models')
    parser.add_argument(
        '--archives',
        nargs='+',
        required=True,
        help='training datasets tgz')
    parser.add_argument(
        '--config',
        required=True,
        help='config tgz')
    parser.add_argument(
        '--bucket',
        required=True,
        help='GCS bucket name to look for archives and config')
    parser.add_argument(
        '--model',
        required=False,
        help='model to train')
    parser.add_argument(
        '--verbosity',
        choices=['DEBUG', 'ERROR', 'FATAL', 'INFO', 'WARN'],
        default='INFO')

    args, _ = parser.parse_known_args()
    return args


class DonkeyTrainer:

    def __init__(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(suffix=None)
        self.datasets = []

    def get_archives(self, bucket_name, archives):
        for archive in self.split_archives_names(archives):
            dataset = util.get_file(bucket_name=bucket_name, blob_name=archive, dest_dir=self.tmpdir.name)
            self.datasets.append(dataset)

    def load_config(self, bucket_name, config_name):
        path = util.get_file(bucket_name=bucket_name, blob_name=config_name, dest_dir=self.tmpdir.name)
        config_path = self.find_config([path])
        print(f"Loading config file from {config_path}")
        self.cfg = dk.load_config(config_path=config_path)
        print(f"   Config file loaded: {config_path}")

    def train_and_evaluate(self, model):
        modelfilepath = os.path.join(self.tmpdir.name, self.cfg.MODELS_PATH)
        os.makedirs(modelfilepath, exist_ok=True)

        tub_paths = self.find_tubs()
        print(f"   Using tubs {tub_paths}")

        if model:
            history = train(self.cfg, tub_paths=tub_paths,
                        model_type=model,
                        transfer=None,
                        comment="")
        else:
            history = train(self.cfg, tub_paths=tub_paths,
                        model_type=self.cfg.DEFAULT_MODEL_TYPE,
                        transfer=None,
                        comment="")

    def save_model(self, ext, bucket_name, blob_name):
        database = PilotDatabase(self.cfg)
        model_name = f"{database.entries[0]['Name']}.{ext}"
        models_dir = os.path.join(self.tmpdir.name, self.cfg.MODELS_PATH)
        model_path = os.path.join(models_dir, model_name)
        util.save_file(model_path, bucket_name, blob_name)

    def split_archives_names(self, archives):
        return [a for st in archives for a in st.split(',')]
    
    def find_tubs(self):
        paths = glob.glob(self.tmpdir.name + '/**/manifest.json', recursive=True)
        return ','.join([str(Path(p).absolute().parent) for p in paths])
    
    def find_config(self, paths):
        for path in paths:
            configs = glob.glob(os.path.join(path, '/**/config.py'), recursive=True)
            if len(configs) > 0:
                return configs[0]
        raise RuntimeError('No config file found')


if __name__ == '__main__':
    try:
        print("Starting training job")
        args = get_args()
        
        project_number = os.environ.get("CLOUD_ML_PROJECT_ID")
        print(f"GCP project : {str(project_number)}")

        gcreds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        print(f"GOOGLE_APPLICATION_CREDENTIALS : {str(gcreds)}")

        tf.compat.v1.logging.set_verbosity(args.verbosity)
        print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
        
        trainer = DonkeyTrainer()
        trainer.get_archives(args.bucket, args.archives)

        trainer.load_config(args.bucket, args.config)
        print(f"TF FLite creation : {trainer.cfg.CREATE_TF_LITE}")
        print(f"ONNX creation : {trainer.cfg.CREATE_ONNX_MODEL}")

        print(f"Training model")
        trainer.train_and_evaluate(args.model)

        print(f"Exporting h5 model")
        now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        blob_name = os.path.join('models', f"pilot-{now}")
        h5_blob_name = f"{blob_name}.h5"
        trainer.save_model(ext='h5', bucket_name=args.job_dir, blob_name=h5_blob_name)

        if trainer.cfg.CREATE_TF_LITE:
            tflite_blob_name = f"{blob_name}.tflite"
            print(f"Exporting tflite model")
            trainer.save_model(ext='tflite', bucket_name=args.job_dir, blob_name=tflite_blob_name)
        
        if trainer.cfg.CREATE_ONNX_MODEL:
            onnx_blob_name = f"{blob_name}.onnx"
            print(f"Exporting onnx model")
            trainer.save_model (ext='onnx', bucket_name=args.job_dir, blob_name=onnx_blob_name)
        
        print('Training job complete.')
    except Exception as exc:
        print(repr(exc))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
