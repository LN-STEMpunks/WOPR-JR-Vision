import cv2
import numpy
import math
import argparse
from enum import Enum
import sys

parser = argparse.ArgumentParser(description='WOPR-JR Vision processing')
parser.add_argument('-c', '--camera', type=int, default=0, help='camera port')
args = parser.parse_args()


hueMin = 73.26
hueMax = 120.20
satMin = 95.09
satMax = 165.78
lumMin = 100.62
lumMax = 320.48

def process(source0):
	"""
	Runs the pipeline and sets all outputs to new values.
	"""
	# Step Blur0:
	source0 = cv2.blur(source0, (4, 4))

	source0 = cv2.cvtColor(source0, cv2.COLOR_BGR2HLS)
	source0 = cv2.inRange(source0, (hueMin, lumMin, satMin),  (hueMax, lumMax, satMax))
	
	contours, hier = cv2.findContours(source0, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
	return contours


 
# Now we can initialize the camera capture object with the cv2.VideoCapture class.
# All it needs is the index to a camera port.
camera = cv2.VideoCapture(args.camera)

camera.set(3,160)
camera.set(4,120)
 
# Captures a single image from the camera and returns it in PIL format
def get_image():
 # read is the easiest way to get a full image out of a VideoCapture object.
 retval, im = camera.read()
 #im = cv2.imread('./before.jpg')
 return im

st, et = 0, 0

import time

while True:
    st = time.time()
    camera_capture = get_image()
    outputim = camera_capture.copy()

    cnts = process(camera_capture)

    if cnts is None:
        cnts = []

    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)

    #outputim = cv2.resize(camera_capture, (160, 120), 0, 0, cv2.INTER_CUBIC)

    centres = []
    if len(cnts) >= 2:
        cv2.drawContours(outputim,cnts,-1,(0,0,255),3)
        cv2.drawContours(outputim,cnts,-2,(0,0,255),3)

	
    #cv2.imwrite(file, outputim)
    cv2.imshow('img', outputim)
	
    et = time.time()

    print ("FPS: %f" % (1.0 / (et - st)))
    sys.stdout.flush()

    k = cv2.waitKey(1)

