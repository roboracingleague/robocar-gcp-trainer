#!/usr/bin/env python3
"""Merge tubs.

Usage:
  merge_tub.py <new_tub> <tub>...

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.

"""
from docopt import docopt

import os
import shutil
import time
import logging
import json
from pathlib import Path
from tqdm import tqdm

from donkeycar.parts.tub_v2 import Tub, TubWriter
from donkeycar.parts.datastore import TubHandler
from donkeycar.pipeline.types import TubRecord

from donkeycar.management.tub import TubManager
from donkeycar.pipeline.types import TubDataset


import donkeycar as dk



class tubProcessor:


    def __init__(self, args, cfg) -> None:

        inputs=['cam/image_array','user/angle', 'user/throttle', 'user/mode', ]
        types=['image_array','float', 'float','str']
#        inputs += ['user/lane', 'user/acc','enc/speed']
#        types += ['int','int','float']
        inputs += ['user/lane']
        types += ['int']
        meta=[]

        shutil.rmtree(args['<new_tub>'],ignore_errors=True)

        self.tub_out = Tub(base_path=args['<new_tub>'], inputs=inputs, types=types, metadata=meta)

        self.cfg = cfg
        self.args = args

    def processRecords(self) -> None:

        for aTub in self.args['<tub>']:
            print (f"Processing tub {aTub}")

            tub_in = Tub(base_path=aTub,
                    inputs=self.tub_out.manifest.inputs ,
                    types=self.tub_out.manifest.types)

            for idx, record in enumerate(tqdm(tub_in)):
                t = TubRecord(self.cfg, tub_in.base_path, record)
                if idx in tub_in.manifest.deleted_indexes:
                    continue
                else:
                    img = t.image()
                    t.underlying['cam/image_array']=img
                    self.tub_out.write_record(t.underlying)

        print (f"Proccessed Tubs saved to {self.args['<new_tub>']}")


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()
    processor = tubProcessor(args, cfg)
    processor.processRecords()