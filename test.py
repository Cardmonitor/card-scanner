from scipy.misc import imread, imresize, imshow
from pprint import pprint
from scan_card import ScanCard
from match_card import compare_cards, hash_original_images, load_orig_image_hashs_from_json

import cv2
import numpy as np
import scan_card
import scipy
import timeit
import json
import os.path

DEFAULTCAM = 0
WEBCAM = 1

cam = cv2.VideoCapture(WEBCAM)

scan_card.setup_windows()
scanCard = ScanCard(cam)

if (os.path.isfile("orig_image_hashs.json")):
    orig_image_hashs = load_orig_image_hashs_from_json()
else:
    orig_image_hashs = hash_original_images()

while True:
    capture = scanCard.check_for_card()

    if capture is not None:
        print "Card captured, proceeding to find a match"
        scanCard.display_snapshot()
        original = compare_cards(capture, orig_image_hashs)
        cv2.imshow("match", original)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2.imwrite('source_images/test.jpg', warped)

cam.release()
cv2.destroyAllWindows()