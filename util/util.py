import os
import zipfile
import re
import numpy as np
import datetime
import json


def to_discrete(a):
    a = a + 1
    b = round(a / (2/14))
    return int(b)


def to_discrete_data(d):
    d[2] = to_discrete(float(d[2]))
    d[1] = to_discrete(float(d[1]))
    return d


def get_data(root,f):
    try:
        d = json.load(open(os.path.join(root,f)))
        if d['user/angle'] == None:
            d['user/angle'] = 0
        return ['user',d['user/throttle'],d['user/angle'],root,d['cam/image_array'], None]
    except Exception as err:
        print('JSON open/parse error {0}'.format(err))
        return None


numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts



def extract_files(work_dir):
    def unzip_file(root,f):
        zip_ref = zipfile.ZipFile(os.path.join(root,f), 'r')
        zip_ref.extractall(root)
        zip_ref.close()

    print('Extracting files')
    # unzip datasets
    for root, _, files in os.walk(work_dir):
        for f in files: 
            if f.endswith('.zip'):
                unzip_file(root, f)


def remap_throttle(data, break_range=10):
    break_throttle = 9
    slow_throttle = 10
    medium_throttle = 12
    high_throttle = 14

    data[:,1] = slow_throttle
    throttle_array = np.copy(np.array(data[:,1], dtype='float32'))
    angle_array = np.array(data[:,2], dtype='float32')
    start_idx = 0
    end_idx = 0
    start_range = False
    for a_idx in range(0, len(angle_array)):
        val = angle_array[a_idx]
        if a_idx < len(angle_array)-3 and throttle_array[a_idx] < 6 and throttle_array[a_idx+1] < 6 and throttle_array[a_idx+2] < 6:
            start_range = False
            for idx in range(a_idx, min(a_idx+10, len(angle_array))):
                data[idx,1] = break_throttle

        if val >= 5 and val <= 10:
            if not start_range: 
                start_range = True
                start_idx = a_idx
            end_idx = a_idx
        else:
            if (end_idx - start_idx) > 80:
                #print('Long line: ' + str(start_idx) + ',' + str(end_idx))
                for idx in range(start_idx, end_idx - break_range):
                    data[idx,1] = high_throttle
            elif (end_idx - start_idx) > 25:
                #print('Short line: ' + str(start_idx) + ',' + str(end_idx))
                for idx in range(start_idx, end_idx - break_range):
                    data[idx,1] = medium_throttle

            start_idx = 0
            end_idx = 0
            start_range = False


def load_data(rootDir, break_range=10):
    print('Loading data')
    data = []
    for root, _, files in os.walk(rootDir):
        data.extend([get_data(root,f) for f in sorted(files, key=numericalSort) if f.startswith('record') and f.endswith('.json')])

    data = np.array([d for d in data if d != None])

    angles = np.array(data[:,2], dtype='float32')
    if np.max(angles) < 2:
        print('load_data mapping to discrete')
        data = [to_discrete_data(d) for d in data]
    data = np.array(data)

    remap_throttle(data, break_range)

    return data


def get_output_pattern(args):
    #out_pattern = '/opt/ml/model/model_cat_{epoch:02d}_{angle_out_loss:.2f}_{val_angle_out_loss:.2f}.h5'
    options = [args.model_name, str(args.slide) + "slide"]
    if args.blur:
        options.append('blur')
    if args.crop:
        options.append('crop' + str(args.crop))
    if args.clahe:
        options.append('clahe')
    options.append(datetime.datetime.now().strftime("%y%m%d_%H%M"))
    return args.job_dir + '/' + '-'.join(options) + '.h5'
    