import os
import random
import json

import numpy as np
import cv2

from keras.preprocessing.image import load_img, img_to_array, save_img
from keras.preprocessing.image import random_shift

from util.util import load_data


def load_image_from_file(path, clahe):
    img = np.array(load_img(path, color_mode= "grayscale"))
    if len(img.shape) > 2 and img.shape[2] != 1:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if clahe:
        claheTransform = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img = claheTransform.apply(img)
    return img.reshape(120,160,1)


def generate_enhanced_dataset(root, destination, images_count, break_range=10, blur=True, crop=0, clahe=True):
    print('Generating enhanced dataset')
    do_random_shift = True
    rnd_lines = True

    data = load_data(root, break_range)

    # load images
    for idx in range(0, len(data)):
        dd = data[idx]
        img = img_to_array(load_image_from_file(os.path.join(dd[3],dd[4]), clahe))
        data[idx,5] = img

    try:
        os.mkdir(destination)
    except:
        pass

    cnt = 0
    # Generate enhanced images
    while cnt < images_count:
        for idx in range(0, len(data)):
            img = data[idx, 5]

            if do_random_shift:
                img = random_shift(img, 0.1, 0.0, row_axis=0, col_axis=1, channel_axis=2) 
            if rnd_lines:
                if random.randint(0,3) == 3:
                    lines_img = np.zeros((120,160), dtype='float32')
                    rnd1 = random.randint(0, 120)
                    rnd2 = random.randint(0, 120)
                    cv2.line(lines_img,(0,rnd1+40),(160,rnd2+40),(256,256,256),2, cv2.LINE_AA)
                    cv2.line(lines_img,(0,rnd1),(160,rnd2),(256,256,256),2, cv2.LINE_AA)
                    cv2.line(lines_img,(0,rnd1-40),(160,rnd2-40),(256,256,256),2, cv2.LINE_AA)

                    img = np.array(cv2.addWeighted(img,0.5,lines_img,0.10,0, dtype=1), dtype='uint8')
            # last transformation
            if blur:
                img = np.array(cv2.bilateralFilter(img,9,75,75), dtype='uint8').reshape(120,160,1)
            # step3
            if crop:
                img[crop:120] = 0

            # save image
            img_filename = '{:08d}_cam-image_array_.jpg'.format(cnt)
            save_img(os.path.join(destination, img_filename), img)
            # save data
            ff = open(os.path.join(destination, 'record_{:08d}.json'.format(cnt)), "w")
            json.dump({ "user/mode": "user", "cam/image_array": img_filename, "user/throttle": data[idx, 1], "user/angle": data[idx, 2] }, ff)
            ff.close()

            cnt = cnt + 1
            if cnt > images_count:
                break
    print('Generate enhanced dataset done')
