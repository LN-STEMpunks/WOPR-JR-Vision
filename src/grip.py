#!/usr/bin/python

import cv2
import numpy
import math
import argparse
import sys


parser = argparse.ArgumentParser(description='WOPR-JR Vision processing')
parser.add_argument('-c', '--camera', type=int, default=0, help='camera port')
parser.add_argument('-show', '--show', action='store_true', help='show processed image')
parser.add_argument('-p', '--publish', action='store_true', help='publish to networktables')
parser.add_argument('-ip', '--address', type=str, default="roboRIO-3966-frc.local", help='network tables address')
parser.add_argument('-did', '--dashboardid', type=str, default="GearPeg", help='smart dashboard publish ID')
parser.add_argument('-t', '--table', type=str, default="vision/gearpeg", help='smart dashboard publish ID')
parser.add_argument('-s', '--size', type=int, nargs=2, default=[160, 120], help='camera size')
parser.add_argument('-f', '--file', default="lab.conf", help='config file')
args = parser.parse_args()

# sets our preferences
exec(open(args.file).read())

def addPoint(p1, p2):
	return (p1[0]+p2[0], p1[1]+p2[1])

if args.publish:
	from networktables import NetworkTables
	NetworkTables.initialize(server=args.address)
	sd = NetworkTables.getTable("SmartDashboard")
	table = NetworkTables.getTable(args.table)


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

camera = None

def init_camera():
        global camera
        camera = cv2.VideoCapture(args.camera)
        while camera is None:
                camera = cv2.VideoCapture(args.camera)

        #camera.set_exposure_auto(0)

        camera.set(3,args.size[0])
        camera.set(4,args.size[1])

def get_image():
        retval, im = camera.read()
        while im is None or not retval:
                print retval
                time.sleep(1)
                init_camera()
                retval, im = camera.read()
	return im

init_camera()
st, et = 0, 0
camst, camet = 0, 0

import time

while True:
	st = time.time()
	camst = time.time()
	camera_capture=get_image()
	camet = time.time()
	if args.show:
		outputim = camera_capture.copy()
        contours = process(camera_capture)
        
	if contours is None:
		contours = []

	center = (-1, -1)

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

	if args.show: cv2.imshow('img', outputim)
	
	k = cv2.waitKey(1)
	et = time.time()
	
	fps = 1.0 / (et - st)
	camfps = 1.0 / (camet - camst)

	if args.publish:
		sd.putString(args.dashboardid, str(center))
		table.putNumber("x", center[0])
		table.putNumber("y", center[1])
		table.putNumber("fps", fps)
		table.putNumber("camfps", camfps)

	sys.stdout.write ("center: (%03d, %03d) fps: %3.1f camfps: %.1f   \r" % (center[0], center[1], fps, camfps))
	sys.stdout.flush()
