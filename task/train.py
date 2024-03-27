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
        '--bucket',
        required=True,
        help='GCS bucket name to look for archives and config, and to export models')
    parser.add_argument(
        '--archives',
        nargs='+',
        required=True,
        help='training datasets tgz, relative to bucket, separated by :')
    parser.add_argument(
        '--config',
        required=False,
        help='config tgz, relative to bucket, use cfg_complete.py by default')
    parser.add_argument(
        '--model',
        required=True,
        help='output model name, relative to bucket, without .tgz extension')
    parser.add_argument(
        '--type',
        required=True,
        help='model type')
    parser.add_argument(
        '--transfer',
        required=False,
        help='transfer model, relative to bucket, with .tgz extension')
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
        self.config_path = None
        self.transfer_path = None
        self.model_path = None
        self.cfg = None

    def get_archives(self, bucket_name, archives):
        for archive in archives:
            util.get_archive(bucket_name=bucket_name, blob_name=archive, dest_dir=self.tmpdir.name)

            archive_name = Path(archive).stem
            archive_dir = os.path.join(self.tmpdir.name, archive_name)
            if not os.path.isdir(archive_dir):
                raise FileNotFoundError(f"Expected directory {archive_name} was not found in archive {archive}")
            
            logger.info(f"Archive extracted to {archive_dir}")
            self.datasets.append(archive_dir)

    def load_config(self, bucket_name, config):
        config_path = os.path.join(self.tmpdir.name, 'config.py')
        if config:
            util.get_archive(bucket_name=bucket_name, blob_name=config, dest_dir=self.tmpdir.name)
        else:
            copyfile(str(files('donkeycar.templates').joinpath('cfg_complete.py')), config_path)
        self.cfg = dk.load_config(config_path=config_path)
        self.config_path = config_path
    
    def get_transfer(self, bucket_name, transfer):
        if transfer:
            util.get_archive(bucket_name, transfer, self.tmpdir.name)
            self.transfer_path = os.path.join(self.tmpdir.name, Path(transfer).stem)
            logger.info(f"Transfer model downloaded to {self.transfer_path}")

    def train_and_evaluate(self, model, model_type=None):
        models_dir = os.path.join(os.path.split(self.config_path)[0], self.cfg.MODELS_PATH)
        self.model_path = os.path.join(models_dir, Path(model).name)
        os.makedirs(models_dir, exist_ok=True)

        tub_paths = ','.join(self.datasets)
        logger.info(f"Using tubs {tub_paths}")

        history = train(self.cfg, tub_paths=tub_paths, model=self.model_path, model_type=model_type, transfer=self.transfer_path)

    def save_models(self, bucket_name, model):
        util.save_to_archive(self.model_path, bucket_name, f"{model}.tgz")

        model_basepath = os.path.splitext(self.model_path)[0]
        blob_basepath, model_ext = os.path.splitext(model)

        if self.cfg.CREATE_TF_LITE and model_ext != '.tflite':
            util.save_to_archive(f"{model_basepath}.tflite", bucket_name, f"{blob_basepath}.tflite.tgz")
        
        if self.cfg.CREATE_TENSOR_RT and model_ext != '.trt':
            logger.info(f"Uploading {model_basepath}.trt to {bucket_name}/{blob_basepath}.trt.tgz")
            util.save_to_archive(f"{model_basepath}.trt", bucket_name, f"{blob_basepath}.trt.tgz")

        if self.cfg.CREATE_ONNX_MODEL and model_ext != '.onnx':
            logger.info(f"Uploading {model_basepath}.onnx to {bucket_name}/{blob_basepath}.onnx.tgz")
            util.save_to_archive(f"{model_basepath}.onnx", bucket_name, f"{blob_basepath}.onnx.tgz")
    
    def cleanup(self):
        self.tmpdir.cleanup()
        self.tmpdir = None

def split_archives_names(archives):
    return [a for st in archives for a in st.split(':')]

def log_args(args, archives):
    logger.info("GOOGLE_CLOUD_PROJECT : {}".format(str(os.environ.get("GOOGLE_CLOUD_PROJECT"))))
    logger.info("CLOUD_ML_PROJECT_ID : {}".format(str(os.environ.get("CLOUD_ML_PROJECT_ID"))))
    logger.info("GOOGLE_APPLICATION_CREDENTIALS : {}".format(str(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))))
    logger.info("archives : {}".format(str(args.archives)))
    logger.info("config : {}".format(str(args.config)))
    logger.info("bucket : {}".format(str(args.bucket)))
    logger.info("model : {}".format(str(args.model)))
    logger.info("type : {}".format(str(args.type)))
    logger.info("transfer : {}".format(str(args.transfer)))
    logger.info("verbosity : {}".format(str(args.verbosity)))
    logger.info("parsed archives names : {}".format(str(archives)))

def main():
    try:
        logger.info("Starting training job")
        args = get_args()

        archives = split_archives_names(args.archives)
        log_args(args, archives)

        tf.compat.v1.logging.set_verbosity(args.verbosity)
        logger.info("Num GPUs Available: {}".format(str(len(tf.config.list_physical_devices('GPU')))))
        
        trainer = DonkeyTrainer()
        trainer.get_archives(args.bucket, archives)

        trainer.load_config(args.bucket, args.config)

        trainer.get_transfer(args.bucket, args.transfer)

        logger.info(f"TF FLite creation : {trainer.cfg.CREATE_TF_LITE}")
        logger.info(f"ONNX creation : {trainer.cfg.CREATE_ONNX_MODEL}")

        trainer.train_and_evaluate(args.model, args.type)

        trainer.save_models(args.bucket, args.model)

        trainer.cleanup()
        
        logger.info('Training job complete')
    except Exception as exc:
        logger.info(repr(exc))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)

if __name__ == '__main__':
    main()
