import numpy as np
import math
import json
import re
import os
import random
import json 
import cv2

from trainer.model import NVidia
from keras import callbacks
from keras.preprocessing.image import load_img, img_to_array


def trim_img(img):
#    img[0:20] = 0
    return img

def linear_bin(a):
    arr = np.zeros(15)
    arr[int(a)] = 1
    return arr
def throttle_bin(a):
    arr = np.zeros(7)
    if int(a) >= 8:
        arr[int(a) - 8] = 1
    return arr
    

def get_dataset(data, slide, enhance):
    ### Loading throttle and angle ###
    angle = [d[2] for d in data]
    throttle = [d[1] for d in data]
    angle_array = np.array(angle)
    throttle_array = np.array(throttle)

    ### Loading images ###
    images = np.array([trim_img(img_to_array(load_img(os.path.join(d[3],d[4]), grayscale=True))) for d in data],'f')
    
    # image before parameters
    images = images[:len(images)-slide]
    angle_array = angle_array[slide:]
    throttle_array = throttle_array[slide:]
        
    return images, angle_array, throttle_array


def slide_data(data, slide):
    shifted_data = data
    thr = np.roll(np.array(data)[:,1], (-1)*slide)
    ang = np.roll(np.array(data)[:,2], (-1)*slide)
    for i in range(0,len(shifted_data)):
        shifted_data[i][2] = ang[i]
        shifted_data[i][1] = thr[i]
    return shifted_data


def get_model(in_model_path):
    model = NVidia()
    model.compile(optimizer='adam',
                loss={'angle_out': 'categorical_crossentropy', 
                        'throttle_out': 'categorical_crossentropy'},
                loss_weights={'angle_out': 0.9, 'throttle_out': 0.9},
                metrics=["accuracy"])
    if in_model_path:
        model.load_weights(in_model_path)
        print('Using model ' + in_model_path)
    return model


def get_callbacks_list(out_model_path):
    logs = callbacks.TensorBoard(log_dir='logs', histogram_freq=0, write_graph=True, write_images=True)
    save_best = callbacks.ModelCheckpoint(out_model_path, monitor='angle_out_loss', verbose=1, save_best_only=True, mode='min', save_weights_only=True)
    early_stop = callbacks.EarlyStopping(monitor='angle_out_loss', 
                                                    min_delta=.0005, 
                                                    patience=20, 
                                                    verbose=1, 
                                                    mode='auto')
    #categorical output of the angle
    #callbacks_list = [save_best, early_stop, logs]
    callbacks_list = [save_best, early_stop]
    return callbacks_list


def train(images, angle_array, throttle_array, out_model_path, in_model_path):
    angle_cat_array = np.array([linear_bin(a) for a in angle_array])
    throttle_cat_array = np.array([throttle_bin(a) for a in throttle_array])
    callbacks_list = get_callbacks_list(out_model_path)
    model = get_model(in_model_path)
    model.fit({'img_in':images},{'angle_out': angle_cat_array, 'throttle_out': throttle_cat_array}, batch_size=32, epochs=100, verbose=1, 
        validation_split=0.2, shuffle=True, callbacks=callbacks_list)
