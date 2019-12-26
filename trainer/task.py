import argparse
import os

import trainer.util as th
from util.util import extract_files
from util.util import load_data
from util.util import get_output_pattern
from preprocessing.preprocess import generate_enhanced_dataset

if __name__ == '__main__':
    """Main function called by AI Platform."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--work-dir',
        required=True,
        help='Directory for staging and working files. '
            'This can be a Google Cloud Storage path.')

    parser.add_argument(
        '--job-dir',
        required=False,
        help='Output directory Directory for job files. '
            'This can be a Google Cloud Storage path.')

    parser.add_argument(
        '--batch-size',
        type=int,
        default=64,
        help='Batch size for training and evaluation.')

    parser.add_argument(
        '--train-max-steps',
        type=int,
        default=1000,
        help='Number of steps to train the model')

    parser.add_argument(
        '--images-count',
        type=int,
        default=0,
        help='Number of images to generate')

    parser.add_argument(
        '--break-range',
        type=int,
        default=10,
        help='Images before break')

    parser.add_argument(
        '--blur',
        type=bool,
        default=True,
        help='Apply blur transform')

    parser.add_argument(
        '--crop',
        type=int,
        default=0,
        help='Pixels level to crop (lower)')

    parser.add_argument(
        '--clahe',
        type=bool,
        default=True,
        help='Apply clazhe transform')

    parser.add_argument(
        '--slide',
        type=int,
        default=2,
        help='Number of images to shift')

    parser.add_argument(
        '--model-name',
        default='roborace',
        help='Model name')

    args = parser.parse_args()

    extract_files(args.work_dir)

    work_dir = args.work_dir
    if args.images_count:
        enhanced_work_dir = os.path.join(args.work_dir, 'enhanced')
        generate_enhanced_dataset(args.work_dir, enhanced_work_dir, args.images_count, args.break_range, args.blur, args.crop, args.clahe)
        work_dir = enhanced_work_dir

    data = load_data(work_dir, args.break_range)

    output_pattern = get_output_pattern(args)

    images, angle_array, throttle_array = th.get_dataset(data, args.slide, False)
    th.train(images, angle_array, throttle_array, output_pattern, None)