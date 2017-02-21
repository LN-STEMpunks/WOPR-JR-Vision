#!/usr/bin/python

import cv2
import numpy
import math
import sys

import argparse

parser = argparse.ArgumentParser(description='WOPR-JR Vision processing')
parser.add_argument('-c', '--camera', type=int, default=0, help='camera port')
parser.add_argument('-show', '--show', action='store_true', help='show processed image')
parser.add_argument('-p', '--publish', action='store_true', help='publish to networktables')
parser.add_argument('-ip', '--address', type=str, default="roboRIO-3966-frc.local", help='network tables address')
parser.add_argument('-did', '--dashboardid', type=str, default="Center of ", help='smart dashboard publish ID')
parser.add_argument('-t', '--table', type=str, default="vision", help='smart dashboard publish ID')

parser.add_argument('-s', '--size', type=int, nargs=2, default=[160, 120], help='camera size')

parser.add_argument('-f', '--file', default="nothing.conf", help='config file')
args = parser.parse_args()

# sets our preferences
exec(open(args.file).read())

def addPoint(p1, p2):
    return (p1[0]+p2[0], p1[1]+p2[1])
def subPoint(p1, p2):
    return (p1[0]-p2[0], p1[1]-p2[1])

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

def largestContours(contours, num=2):
    def keyFunc(contour):
        v = cv2.contourArea(contour)
        return v
    return sorted(contours, key=keyFunc, reverse=True)[0:num]

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

def set_exposure(ex):
    import os
    cmd = "v4l2-ctl -d /dev/video%d -c exposure_auto=1 -c exposure_absolute=%s" % (args.camera, str(ex))
    os.system(cmd)
    import time
    time.sleep(.125)

def init_camera():
    global camera
    
    set_exposure(exposure)
    
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



def bestPegFit(contours):
    import math
    min_indexes = (-1, -1)
    min_fitness = float('inf')
    def fitness(c1, c2, a1, a2):
        fromcenter = abs((2.0*c1[1]-args.size[1])/args.size[1])**2 + abs((2.0*c2[1]-args.size[1])/args.size[1])**2
        diff = subPoint(c1, c2)
        diffangle = math.degrees(abs(math.atan2(diff[1], diff[0])))
        if diffangle > 90:
            diffangle = abs(180 - diffangle)
        if diff[0] == 0:
            diffratio = 0
        else:
            diffratio = abs(float(diff[1]) / diff[0])
        if 0 in [a1, a2]:
            diffarea = 0
        else:
            diffarea = a1 / a2
            if diffarea < 1.0:
                diffarea = 1.0 / diffarea
        if diffangle > 18:
            return float('inf')
        return 20*diffangle + 50*diffratio + 120*diffarea + 20*fromcenter
    for i in range(0, len(contours)):
        ic = contourCenter(contours[i])
        ia = cv2.contourArea(contours[i])
        for j in range(i+1, len(contours)):
            jc = contourCenter(contours[j])
            ja = cv2.contourArea(contours[j])
            fit = fitness(jc, ic, ja, ia)
            if fit < min_fitness:
                min_indexes = (i, j)
                min_fitness = fit
    if -1 in min_indexes:
        return (None, float('inf'))

    return (tuple([contours[i] for i in min_indexes]), min_fitness)

def bestHighgoalFit(contours):
    import math
    min_indexes = (-1, -1)
    min_fitness = float('inf')
    def fitness(c1, c2, a1, a2):
        diff = subPoint(c1, c2)
        diffangle = math.degrees(abs(math.atan2(diff[1], diff[0])))
        if diffangle > 90:
            diffangle = abs((180 - diffangle)-90)
        if diff[0] == 0:
            diffratio = 0
        else:
            diffratio = abs(float(diff[1]) / diff[0])
        if 0 in [a1, a2]:
            diffarea = 0
        else:
            diffarea = a1 / a2
            if diffarea < 1.0:
                diffarea = 1.0 / diffarea
        if diffangle > 18:
            return float('inf')
        return 30*diffangle + 60*diffratio + 120*diffarea
    for i in range(0, len(contours)):
        ic = contourCenter(contours[i])
        ia = cv2.contourArea(contours[i])
        for j in range(i+1, len(contours)):
            jc = contourCenter(contours[j])
            ja = cv2.contourArea(contours[j])
            fit = fitness(jc, ic, ja, ia)
            if fit < min_fitness:
                min_indexes = (i, j)
                min_fitness = fit
    if -1 in min_indexes:
        return (None, float('inf'))

    return (tuple([contours[i] for i in min_indexes]), min_fitness)



init_camera()
st, et = 0, 0
camst, camet = 0, 0

import time

while True:
    try:
        st = time.time()
        camst = time.time()
        camera_capture=get_image()
        camet = time.time()
        if args.show:
                outputim = camera_capture.copy()
        contours = process(camera_capture)
        fitness = float('inf')

        targetName=""
        
        if contours is None:
                contours = []

        center = (-1, -1)

        if len(contours) >= 2:
                contours = [j for j in largestContours(contours, 4)]
                pegContours, pegFitness = bestPegFit(contours)
                goalContours, goalFitness = bestHighgoalFit(contours)

                if pegContours and pegFitness < goalFitness and len(pegContours) >= 2:
					contours = pegContours
					fitness = pegFitness
					targetName = "gearpeg"

                if goalContours and goalFitness <= pegFitness and len(goalContours) >= 2:
					contours = goalContours
					fitness = goalFitness
					targetName = "highgoal"

                if contours and len(contours) >= 2:
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

        if (fitness > 10000):
                fitness = 10000

        if args.publish and fitness <= 200:
                stable = table.getSubTable(targetName)
                if not sd.putString(args.dashboardid + targetName, str(center)):
					sd.delete(args.dashboardid)
					print ("Couldn't publish to smart dashboard\n")
					
					worked = True
					worked = worked and stable.putNumber("fitness", fitness)

					worked = worked and stable.putNumber("x", center[0])
					worked = worked and stable.putNumber("y", center[1])
					
					worked = worked and stable.putNumber("fps", fps)

					worked = worked and stable.putNumber("camfps", camfps)
					worked = worked and stable.putNumber("camwidth", args.size[0])
					worked = worked and stable.putNumber("camheight", args.size[1])

					worked = worked and stable.putNumber("time", time.time())

					if not worked:
						print ("Error while writing to table\n")

        sys.stdout.write ("center: (%03d, %03d) fitness: %05d fps: %3.1f camfps: %.1f   \r" % (center[0], center[1], int(fitness), fps, camfps))
        sys.stdout.flush()
    except Exception:
        time.sleep(1.0)
        pass
