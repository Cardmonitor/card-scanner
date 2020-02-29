# -*- coding: utf-8 -*-

from glob import glob
from cv_utils import compare_images
from scipy.misc import imread, imresize, imshow

import cv2
import numpy as np
import scipy
import timeit
import json
import os.path

def dhash(image, hashSize=8):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # resize the input image, adding a single column (width) so we
    # can compute the horizontal gradient
    resized = cv2.resize(image, (hashSize + 1, hashSize))

    # compute the (relative) horizontal gradient between adjacent
    # column pixels
    diff = resized[:, 1:] > resized[:, :-1]

    # convert the difference image to a hash
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

def img_gray(image):
    return np.average(image, weights=[0.299, 0.587, 0.114], axis=2)

def resize(image, height=30, width=30):
    row_res = cv2.resize(image,(height, width), interpolation = cv2.INTER_AREA).flatten()
    col_res = cv2.resize(image,(height, width), interpolation = cv2.INTER_AREA).flatten('F')
    return row_res, col_res

def intensity_diff(row_res, col_res):
    difference_row = np.diff(row_res)
    difference_col = np.diff(col_res)
    difference_row = difference_row > 0
    difference_col = difference_col > 0
    return np.vstack((difference_row, difference_col)).flatten()

def difference_score(image, height = 30, width = 30):
    gray = img_gray(image)
    row_res, col_res = resize(gray, height, width)
    difference = intensity_diff(row_res, col_res)

    return difference.tolist()

def hamming_dist(h1,h2):
    return scipy.spatial.distance.hamming(h1, h2)

def save_orig_image_hashs_to_json(orig_image_hashs):
    data = json.dumps(orig_image_hashs)
    f = open("orig_image_hashs.json","w")
    f.write(data)
    f.close()

def load_orig_image_hashs_from_json():
    print 'Lade Hashes'
    with open("orig_image_hashs.json") as f:
        cards = json.load(f)

    return cards

def hash_original_images():
    print 'Creating Hashes'
    orig_image_hashs = {}
    i = 0
    start = timeit.default_timer()
    for orig in glob("original/*.jpg"):
        if (i > 10000000):
            break
        orig_image = imread(orig)
        orig_image_hash = difference_score(orig_image, 32, 32)
        orig_image_hashs[orig] = orig_image_hash
        i += 1

    stop = timeit.default_timer()
    print('{} Hashes created'.format(i))
    print 'Dauer: ' + str(round((stop - start), 2)) + ' Sekunden'

    save_orig_image_hashs_to_json(orig_image_hashs)

    return orig_image_hashs

if (os.path.isfile("orig_image_hashs.json")):
    orig_image_hashs = load_orig_image_hashs_from_json()
else:
    orig_image_hashs = hash_original_images()

# hash our warped image
#hash = imagehash.phash_simple(Image.open("source_images/test.jpg"))
image = imread("source_images/test.jpg")
# image = cv2.resize(image, (672, 936))
# image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# image_dst = cv2.dct(np.float32(image)/255.0)
image_hash = difference_score(image, 32, 32)

scores = {}
start = timeit.default_timer()
print 'Comparing Hashes'
# loop over all official images
for (filename) in orig_image_hashs:
    # score = compare_images(orig_image, image)
    print(filename)
    scores[filename] = hamming_dist(image_hash, orig_image_hashs[filename])
    # print('Comparing image to {}, score {}'.format(
    #     orig, score
    # ))
stop = timeit.default_timer()
print 'Hashes compared'
print 'Dauer: ' + str(round((stop - start), 2)) + ' Sekunden'
print('-' * 50)
for (filename, score) in sorted(scores.items(), key=lambda item: item[1]):
    print('Comparing image to {}, score {}'.format(
        filename, score
    ))
