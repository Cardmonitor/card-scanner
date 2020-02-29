import numpy as np
import cv2
from skimage.measure import compare_ssim
import imutils

def img_from_buffer(buffer):
    np_arr = numpy.fromstring(buffer,'uint8')
    np_mat = cv2.imdecode(np_arr,0)
    return cv2.fromarray(np_mat)

def show_scaled(win, img):
    min, max, pt1, pt2 = cv2.MinMaxLoc(img)
    cols, rows = img.shape[:2]
    tmp = cv2.CreateMat(rows, cols,cv2.CV_32FC1)
    cv2.Scale(img, tmp, 1.0/(max-min), 1.0*(-min)/(max-min))
    cv2.ShowImage(win,tmp)

def float_version(img):
    return cv2.convertScale(img, 1/255.0)

def compare_images(img1, img2):
    score, diff = compare_ssim(img1, img2, full=True)
    return score

def sum_squared(img1, img2):
    score, diff = compare_ssim(img1, img2, full=True)
    return score

def ccoeff_normed(img1, img2):
    size = cv2.getSize(img1)
    tmp1 = float_version(img1)
    tmp2 = float_version(img2)

    cv2.subS(tmp1, cv2.Avg(tmp1), tmp1)
    cv2.subS(tmp2, cv2.Avg(tmp2), tmp2)

    norm1 = tmp1.copy()
    norm2 = tmp2.copy()
    cv2.Pow(tmp1, norm1, 2.0)
    cv2.Pow(tmp2, norm2, 2.0)

    #cv2.Mul(tmp1, tmp2, tmp1)

    return cv2.dotProduct(tmp1, tmp2) /  (cv2.sum(norm1)[0]*cv2.sum(norm2)[0])**0.5

def clone_image(img):
    return img.copy()

def overlay_text_on_image(img,text,font,pos=(1,24),color=(255,255,255)):
    x = pos[0]
    y = pos[1]
    chunk = 100
    line = text[0:chunk]
    length = len(text)
    pos = chunk

    while True:
        cv2.putText(img, "%s" % line, (x,y), font, 1, color, 2, cv2.LINE_AA)
        if pos >= length:
            break;
        line = text[pos:(pos+chunk)]
        pos = pos + chunk
        y = y + 24

def flip_image(img):
    return cv2.flip(img, -1)

def to_gray_image(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


