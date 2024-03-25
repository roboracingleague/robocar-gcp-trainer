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

import logging
from sys import stdout

def console_config(level):
    root_logger = logging.getLogger('')
    root_logger.setLevel(level)
    console = logging.StreamHandler(stdout)
    console.setFormatter(logging.Formatter('%(asctime)s %(levelname)-.1s %(filename)s:%(funcName)s %(message)s'))
    root_logger.addHandler(console)

    logger = logging.getLogger(__name__)
    return logger

logger = console_config(logging.INFO)

# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function

import os
import sys
import argparse
import traceback
import tempfile
from datetime import datetime
from pathlib import Path
from importlib_resources import files
import tensorflow as tf
from shutil import copyfile

import donkeycar as dk
from donkeycar.pipeline.training import train
from donkeycar.pipeline.database import PilotDatabase

from . import util


def get_args():
    """Argument parser.

    Returns:
      Dictionary of arguments.
    """
    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     '--job-dir',
    #     required=True,
    #     help='local or GCS location for writing checkpoints and exporting models')
    parser.add_argument(
        '--archives',
        nargs='+',
        required=True,
        help='training datasets tgz')
    parser.add_argument(
        '--config',
        required=False,
        help='config tgz, use cfg_complete.py by default')
    parser.add_argument(
        '--bucket',
        required=True,
        help='GCS bucket name to look for archives and config, and to export models')
    parser.add_argument(
        '--model',
        required=False,
        help='output model name')
    parser.add_argument(
        '--type',
        required=True,
        help='model type')
    parser.add_argument(
        '--transfer',
        required=False,
        help='transfer model')
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
        self.transfer_path = None

    def get_archives(self, bucket_name, archives):
        for archive in self.split_archives_names(archives):
            dataset = util.get_archive(bucket_name=bucket_name, blob_name=archive, dest_dir=self.tmpdir.name)
            self.datasets.append(dataset)

    def load_config(self, bucket_name, config_name):
        if config_name is not None:
            path = util.get_archive(bucket_name=bucket_name, blob_name=config_name, dest_dir=self.tmpdir.name)
            config_path = self.find_config([path])
        else:
            config_path = os.path.join(self.tmpdir.name, 'config.py')
            copyfile(str(files('donkeycar.templates').joinpath('cfg_complete.py')), config_path)
        self.cfg = dk.load_config(config_path=config_path)
    
    def get_transfer(self, bucket_name, transfer):
        if transfer is not None:
            self.transfer_path = util.get_model(bucket_name, transfer, self.tmpdir.name)

    def train_and_evaluate(self, model_type=None):
        modelfilepath = os.path.join(self.tmpdir.name, self.cfg.MODELS_PATH)
        os.makedirs(modelfilepath, exist_ok=True)

        tub_paths = ','.join(self.datasets)
        logger.info(f"Using tubs {tub_paths}")

        history = train(self.cfg, tub_paths=tub_paths, model=None, model_type=model_type, transfer=self.transfer_path)

    def save_model(self, ext, bucket_name, blob_name):
        database = PilotDatabase(self.cfg)
        model_name = f"{database.entries[0]['Name']}.{ext}"
        model_path = os.path.join(self.tmpdir.name, self.cfg.MODELS_PATH, model_name)
        util.save_file(model_path, bucket_name, f"{blob_name}.{ext}")

    def split_archives_names(self, archives):
        return [a for st in archives for a in st.split(',')]
    
    def find_tubs(self):
        paths = [str(x) for x in Path(self.tmpdir.name).rglob('manifest.json')]
        return ','.join([str(Path(p).absolute().parent) for p in paths])
    
    def find_config(self, paths):
        for path in paths:
            configs = [str(x) for x in Path(path).rglob('config.py')]
            if len(configs) > 0:
                return configs[0]
        raise RuntimeError('No config file found')


if __name__ == '__main__':
    try:
        logger.info("Starting training job")
        args = get_args()
        
        logger.info("GOOGLE_CLOUD_PROJECT : {}".format(str(os.environ.get("GOOGLE_CLOUD_PROJECT"))))
        logger.info("CLOUD_ML_PROJECT_ID : {}".format(str(os.environ.get("CLOUD_ML_PROJECT_ID"))))
        logger.info("GOOGLE_APPLICATION_CREDENTIALS : {}".format(str(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))))

        tf.compat.v1.logging.set_verbosity(args.verbosity)
        logger.info("Num GPUs Available: {}".format(str(len(tf.config.list_physical_devices('GPU')))))
        
        trainer = DonkeyTrainer()
        trainer.get_archives(args.bucket, args.archives)

        trainer.load_config(args.bucket, args.config)

        trainer.get_transfer(args.bucket, args.transfer)

        logger.info(f"TF FLite creation : {trainer.cfg.CREATE_TF_LITE}")
        logger.info(f"ONNX creation : {trainer.cfg.CREATE_ONNX_MODEL}")

        trainer.train_and_evaluate(args.type)

        logger.info(f"Exporting h5 model")
        default_blob_name = os.path.join('models', 'pilot-{}'.format(datetime.now().strftime('%Y%m%d-%H%M%S')))
        trainer.save_model('h5', args.bucket, args.model if args.model else default_blob_name)

        if trainer.cfg.CREATE_TF_LITE:
            logger.info(f"Exporting tflite model")
            trainer.save_model('tflite', args.bucket, args.model if args.model else default_blob_name)
        
        if trainer.cfg.CREATE_ONNX_MODEL:
            logger.info(f"Exporting onnx model")
            trainer.save_model ('onnx', args.bucket, args.model if args.model else default_blob_name)
        
        logger.info('Training job complete')
    except Exception as exc:
        logger.info(repr(exc))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
