import cv2
import numpy
import math
import argparse
import sys


parser = argparse.ArgumentParser(description='WOPR-JR Vision processing')
parser.add_argument('-c', '--camera', type=int, default=0, help='camera port')
parser.add_argument('-show', '--show', action='store_true', help='show processed image')
parser.add_argument('-p', '--publish', action='store_true', help='publish to networktables')
parser.add_argument('-ip', '--address', type=str, default="roboRIO-3966-frc.local", help='publish to networktables')
parser.add_argument('-s', '--size', type=int, nargs=2, default=[160, 120], help='camera port')
args = parser.parse_args()

if args.publish:
	from networktables import NetworkTables
	NetworkTables.initialize(server=args.address)
	sd = NetworkTables.getTable("SmartDashboard")

hueMin = 73.26
hueMax = 120.20
satMin = 95.09
satMax = 140.78
lumMin = 100
lumMax = 250

def addPoint(p1, p2):
	return (p1[0]+p2[0], p1[1]+p2[1])

# TODO: Test best value
blur = (6, 6)

def contourCenter(contour):
	try:
		mu = cv2.moments(contour, False) 
		return ( mu["m10"]/mu["m00"] , mu["m01"]/mu["m00"] )
	except:
		return (0, 0)

def twoLargestContours(contours):
	idx1, idx2, area1, area2 = 0, 0, -1, -1
	for i in range(0, len(contours)):
		areai = cv2.contourArea(contours[i])
		if (areai > area1):
			area2 = area1
			idx2 = idx1

			area1 = areai
			idx1 = i
		elif (areai > area2):
			area2 = areai
			idx2 = i
	return (idx1, idx2)

def process(source0):
	"""
	Runs the pipeline and sets all outputs to new values.
	"""
	# Step Blur0:
	source0 = cv2.blur(source0, blur)

	source0 = cv2.cvtColor(source0, cv2.COLOR_BGR2HLS)
	source0 = cv2.inRange(source0, (hueMin, lumMin, satMin),  (hueMax, lumMax, satMax))
	
	contours, hier = cv2.findContours(source0, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
	return contours

camera = cv2.VideoCapture(args.camera)


#camera.set_exposure_auto(0)

camera.set(3,args.size[0])
camera.set(4,args.size[1])

def get_image():
	retval, im = camera.read()
	return im

st, et = 0, 0

import time

while True:
	st = time.time()

	camera_capture = get_image()
	if args.show:
		outputim = camera_capture.copy()

	contours = process(camera_capture)

	if contours is None:
		contours = []

	center = [-1, -1]
	if len(contours) >= 2:
		contours = [contours[j] for j in twoLargestContours(contours)]
		centers = [contourCenter(j) for j in contours]
		center = (int((centers[0][0] + centers[1][0])//2), int((centers[0][1] + centers[1][1])//2))
		
		if args.show:
			cv2.drawContours(outputim,contours, 0, (255, 120, 0), 2)
			cv2.drawContours(outputim,contours, 1, (255, 120, 0), 2)
			cv2.line(outputim, addPoint(center, (0, -4)), addPoint(center, (0, 4)), (0, 0, 255), 1)
			cv2.line(outputim, addPoint(center, (-4, 0)), addPoint(center, (4, 0)), (0, 0, 255), 1)
			cv2.circle(outputim, center, 5, (0, 0, 255), 1)
			#cv2.rectangle(outputim, addPoint(center, (-1, -3)), addPoint(center, (+1, +3)), (0, 0, 255), 2)
	if args.show:	
		cv2.imshow('img', outputim)
	k = cv2.waitKey(1)
	
	
	et = time.time()
	if args.publish:
		sd.putString("GearPegString", str(center))

	print ("FPS: %f" % (1.0 / (et - st)))
	print ("center: (%d, %d)" % (center[0], center[1]))
	sys.stdout.flush()
