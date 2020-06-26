import imutils
from skimage.filters import threshold_adaptive
from scipy.spatial import distance as dist
import numpy as np
import cv2
import os
import camelot
import random
import math
import subprocess
 
def order_points(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    print(xSorted)
    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    (br, tr) = rightMost[np.argsort(D)[::-1], :]

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    print(pts)
    rect = order_points(pts)
    print(rect)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped


def scan_form(form_name, form_image_path):

    # load the image and compute the ratio of the old height
    # to the new height, clone it, and resize it
    image = cv2.imread(form_image_path)
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)
    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('grOrg', gray)
    # gray = cv2.erode(gray, (3, 3))
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # cv2.imshow('gr', gray)
    # cv2.waitKey(0)
    edged = cv2.Canny(gray, 0, 100)
    # cv2.imshow('edge', edged)
    # cv2.waitKey(0)

    # show the original image and the edge detected image
    print("STEP 1: Edge Detection")
    # cv2.imshow("Image", image)
    # cv2.imshow("Edged", edged)

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    cntHull = [ cv2.convexHull(c) for c in cnts ]
    cnts = sorted(cntHull, key=cv2.contourArea, reverse=True)

    print("Found contours")

    # loop over the contours
    for i in range(len(cnts)):
        # approximate the contour
        # if heir[0][i][3] == -1:
        c = cnts[i]
        print(c[0][0], cv2.contourArea(c))
        
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # cv2.imshow('kk', cv2.drawContours(image, [approx], -1, (0, 255, 0), 2))
        # print(c)
        # cv2.waitKey(0)
        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        print(len(approx))
        if len(approx) >= 4:
            screenCnt = approx
            break
    
    # show the contour (outline) of the piece of paper
    print("STEP 2: Find contours of paper")
    cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
    # cv2.imshow("Outline", image)
    print(screenCnt)
    # cv2.waitKey(0)
    # screenCnt = np.array([[[252, 40], [65, 86], [334, 340], [141, 387]]])

    # apply the four point transform to obtain a top-down
    # view of the original image
    warped = four_point_transform(orig, screenCnt.reshape(
        int(screenCnt.shape[0] * screenCnt.shape[1] * screenCnt.shape[2] / 2), 2) * ratio)

    # convert the warped image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    # warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    # warped = threshold_adaptive(warped, 251, offset = 10)
    # warped = warped.astype("uint8") * 255

    # show the original and scanned images
    print("STEP 3: Apply perspective transform")
    # cv2.imshow("Original", orig)
    # cv2.imshow("Scanned", warped)


    print("SAVE")
    # cv2.imwrite("scanned.jpg", imutils.resize(warped, height = 450))
    # cv2.imwrite("scanned.jpg", warped)
    print("CROP")

    # cv2.imshow('Sometitle', warped)

    img = warped
    height, width, channels = img.shape
    end_h = int(height - 10)
    end_w = int(width - 10)

    crop_img = img[10:end_h, 10:end_w]

    print("SAVE CROP")
    # cv2.waitKey(0)

    # APP_ROOT = os.path.dirname(os.path.abspath(_file_))
    # UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/submission')
    filename = form_name if form_name[-4:] == ".jpg" else form_name + ".jpg"
    # final_filename = '%s/%s_%s_scanned.jpg' % (UPLOAD_FOLDER, random.randint(3000, 4000), form_name)
    cv2.imwrite(filename, crop_img)

    # print("Done")

    w = crop_img.shape[0]
    h = crop_img.shape[1]

    return w, h , filename
    cv2.waitKey(0)


import argparse
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image file")
ap.add_argument("-o", "--output",
	help = "file to save the image to")
args = vars(ap.parse_args())
scan_form(args["output"], args["image"])