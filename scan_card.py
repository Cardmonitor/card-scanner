import math
import cv2
import os
import numpy as np
import cv2
from detect_card import find_card
from cv_utils import float_version, show_scaled, sum_squared, ccoeff_normed, clone_image, overlay_text_on_image, flip_image, to_gray_image
import uuid

def order_points(corners):

    pts = np.array(corners)
    print 'points: ', pts
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect

def get_card(color_capture, corners):
    height = 936
    width = 672

    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]], dtype = "float32")
    mat = cv2.getPerspectiveTransform(order_points(corners), dst)
    return cv2.warpPerspective(color_capture, mat, (width, height))

def setup_windows():
    cv2.namedWindow('background')
    cv2.namedWindow('snapshot')
    cv2.namedWindow('main')
    cv2.namedWindow('match')

    cv2.moveWindow('snapshot', 750, 550)
    cv2.moveWindow('match', 1200, 550)
    cv2.moveWindow('background', 50, 500)
    cv2.waitKey(10)
    #cv2.StartWindowThread()


def save_captures(num, captures):
    dir = "data/capture_%02d" % num
    if not os.path.exists(dir):
        os.mkdir(dir)
    for i, img in enumerate(captures):
        path = os.path.join(dir, "card_%04d.png" % i)
        if os.path.exists(path):
            raise Exception("path %s already exists!" % path)
        cv2.SaveImage(path, img)

def cv2array(im):
    depth2dtype = {
        cv2.IPL_DEPTH_8U: 'uint8',
        cv2.IPL_DEPTH_8S: 'int8',
        cv2.IPL_DEPTH_16U: 'uint16',
        cv2.IPL_DEPTH_16S: 'int16',
        cv2.IPL_DEPTH_32S: 'int32',
        cv2.IPL_DEPTH_32F: 'float32',
        cv2.IPL_DEPTH_64F: 'float64',
    }

    arrdtype=im.depth
    a = numpy.fromstring(im.tostring(), dtype=depth2dtype[im.depth], count=im.width*im.height*im.nChannels)
    a.shape = (im.height,im.width,im.nChannels)
    return a

class ScanCard:
    def __init__(self, camera):
        self.recent_frames_max = 3
        self.camera = camera
        self.last_frame = None
        self.last_frame_flipped = None
        self.last_frame_gray = None
        self.recent_frames = []
        self.recent_frames_gray = []
        self.snapshot = None
        self.background = None
        self.background_flipped = None
        self.last_frame = None
        self.size = None
        self.num_pixels = None
        self.snapshot = None
        self.has_moved = None
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def update_snapshot_window(img):
        tmp = cv2.cloneImage(img)
        cv2.putText(tmp, "%s" % (snapshot), (1,24), self.font, (255,255,255))
        cv2.imshow("snapshot", tmp)

    def grab_frame(self):
        ret, frame = self.camera.read()
        frame_gray = to_gray_image(frame)
        frame_flipped = flip_image(frame)

        # Set the size of things if this is the first image we have seen
        if self.last_frame is None:
            self.size = frame.shape
            self.num_pixels = self.size[0]*self.size[1]

        self.recent_frames_gray.append(frame_gray)
        self.recent_frames.append(frame)
        if len(self.recent_frames) > self.recent_frames_max:
            del self.recent_frames[0]
            del self.recent_frames_gray[0]

        self.last_frame = clone_image(frame)
        self.last_frame_flipped = frame_flipped
        self.last_frame_gray = frame_gray
        return frame


    def display_background(self, text=None):
        if text is not None:
            overlay_text_on_image(self.background_flipped, text, self.font)
        cv2.imshow('background', self.background_flipped)

    def display_live(self, text=None):
        if text is not None:
            overlay_text_on_image(self.last_frame_flipped, text, self.font)
        cv2.imshow('main', self.last_frame_flipped)

    def display_snapshot(self):
        if self.snapshot is not None:
            cv2.imshow('snapshot', self.snapshot)
            # cv2.imwrite('source_images/' + str(uuid.uuid4()) + '.jpg', self.snapshot)

    def update_background(self, frame=None):
        if frame is None:
            frame = self.last_frame
            if frame is None:
                frame = self.grab_frame()
        self.background = clone_image(frame)

        self.background_gray = to_gray_image(self.background)
        self.background_flipped = flip_image(self.background)

    def calc_biggest_diff(self):
        return min(sum_squared(self.last_frame_gray, frame) for frame in self.recent_frames_gray)

    def calc_background_similarity(self):
        return min(sum_squared(self.background_gray, frame) for frame in self.recent_frames_gray)

    def check_for_card(self):
        found = False
        base_corr = 0

        self.grab_frame()
        # if the user didn't set the background, get the first frame and consider it the background
        if self.background is None:
            print "Updating background on the account of it being None"
            self.update_background()

        history_diff = self.calc_biggest_diff()
        # Detect movement
        if history_diff < 0.9:
            self.has_moved = True

        # No movement now, but there was before
        elif self.has_moved == True:
            base_corr = self.calc_background_similarity()
            print base_corr
            # Looking at the background, false alarm
            # set the frame as the new background, this helps with lightning change
            if base_corr >= 0.95:
                #self.update_background()
                self.has_moved = False
            else:
                # background and current frame are < 25% similar
                warped = find_card(self.last_frame)
                if warped is not None:
                    self.snapshot = warped
                    # self.snapshot = flip_image(self.snapshot)
                    found = True
                    self.has_moved = False
                else:
                    self.has_moved = False

        self.display_background()
        self.display_live("%.4f [0-10 stable, >10 unstable] | %.4f [>0.75 is background, <0.75 contains foreground]" % (history_diff, base_corr))

        if found is True:
            return clone_image(self.snapshot)
        return None

