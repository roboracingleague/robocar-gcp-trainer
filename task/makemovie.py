
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
from donkeycar.management.makemovie import MakeMovie

def get_args():
    """Argument parser.

    Returns:
      Dictionary of arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out',
        type=str,
        required=False,
        default='tub_movie.mp4',
        help='config file')
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
        '--salient',
        action='store_true',
        required=False,
        help='bucket name to use')
    parser.add_argument(
        '--type',
        type=str,
        required=False,
        help='bucket name to use')
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='bucket name to use')
    parser.add_argument(
        '--start',
        type=int,
        required=False,
        default=0,
        help='bucket name to use')
    parser.add_argument(
        '--end',
        type=int,
        required=False,
        default=-1,
        help='bucket name to use')
    parser.add_argument(
        '--scale',
        type=int,
        default=2,
        required=False,
        help='bucket name to use')
    parser.add_argument(
        '--draw_user_input',
        required=False,
        action='store_true',
        help='bucket name to use')
    parser.add_argument(
        '--verbosity',
        choices=['DEBUG', 'ERROR', 'FATAL', 'INFO', 'WARN'],
        default='INFO')

    args, _ = parser.parse_known_args()
    return args


class donkeyArgs():
    def __init__(self, tub, config, model, type, salient, start, end, scale, draw_user_input, out):
        self.tub = tub
        self.config = config
        self.model = model
        self.type = type
        self.salient = salient
        self.start = start
        self.end = end
        self.scale = scale
        self.draw_user_input = draw_user_input
        self.out = out

class DonkeyMovie:

    def __init__(self) -> None:
        self.mm=MakeMovie()
        self.tmpdir = "."

    def get_archive(self):
        self.tmpdir = util.get_archive(bucket_name=args.bucket, url=args.archive)

    def get_model(self):
        self.modeldir = util.get_model(bucket_name=args.bucket, url=args.model)

    def get_config(self):
        self.cfg_path = os.path.join(self.tmpdir, "config.py")
        self.cfg = dk.load_config(config_path=os.path.join(self.tmpdir, "config.py"))
        self.tub_path = self.tmpdir

    def makemovie(self, model_type, model_file, salient, start, end, scale, draw_user_input, out):

        self.tub_path  = self.tmpdir
        moviesfilepath=os.path.join(self.tmpdir, "movies")
        os.makedirs(moviesfilepath, exist_ok=True)
        self.movies_path = moviesfilepath
        self.movie_file = out
        self.output_file = f"{self.movies_path}/{self.movie_file}"
        mmargs=donkeyArgs(tub=self.tub_path, config=self.cfg_path,model=f"{self.modeldir}/model.h5",type=model_type,salient=salient,start=start,end=end,scale=scale,draw_user_input=draw_user_input, out=self.output_file)
        self.mm.run(mmargs, parser=None)

    def save_movie(self, bucket, storedfile):
        util.save_movie(bucket, self.movies_path, src_filename=self.movie_file, dst_filename=storedfile)
        print(f"Model {self.movies_path}/{self.movie_file} exported to bucket {bucket} as {storedfile}")

if __name__ == '__main__':
    args = get_args()

    tf.compat.v1.logging.set_verbosity(args.verbosity)
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    movie = DonkeyMovie()
    print(f"Download data set archive {args.archive}")
    movie.get_archive()
    print(f"Download model {args.model}")
    movie.get_model()
    print(f"Getting config files from archive")
    movie.get_config()
    print(f"Making movie")
    movie.makemovie(model_type=args.type, model_file=args.model, salient=args.salient, start=args.start, end=args.end, scale=args.scale, draw_user_input=args.draw_user_input, out=args.out)
    print(f"Exporting video")
    movie.save_movie (bucket=args.bucket, storedfile=args.out)
