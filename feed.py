import cv2
import numpy as np
from pprint import pprint
import scan_card

DEFAULTCAM = 0
WEBCAM = 1

cap = cv2.VideoCapture(WEBCAM)

while True:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)

    _, contours, _ = cv2.findContours(thresh,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    sorted_contours = sorted([ (cv2.contourArea(i), i) for i in contours ], key=lambda a:a[0], reverse=True)

    # for _, contour in sorted_contours:
    #     cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)

    if len(sorted_contours) > 1:
        _, card_contour = sorted_contours[1]
        # cv2.drawContours(frame, [card_contour], -1, (0, 255, 0), 2)

        rect = cv2.minAreaRect(card_contour)
        points = cv2.boxPoints(rect)
        points = np.int0(points)

        for point in points:
            cv2.circle(frame, tuple(point), 10, (0,255,0), -1)

        # create a min area rectangle from our contour
        _rect = cv2.minAreaRect(card_contour)
        box = cv2.boxPoints(_rect)
        box = np.int0(box)

        # create empty initialized rectangle
        rect = np.zeros((4, 2), dtype = "float32")

        # get top left and bottom right points
        s = box.sum(axis = 1)
        rect[0] = box[np.argmin(s)]
        rect[2] = box[np.argmax(s)]

        # get top right and bottom left points
        diff = np.diff(box, axis = 1)
        rect[1] = box[np.argmin(diff)]
        rect[3] = box[np.argmax(diff)]

        (tl, tr, br, bl) = rect

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(frame, M, (maxWidth, maxHeight))

    cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2.imwrite('source_images/test.jpg', warped)

cap.release()
cv2.destroyAllWindows()