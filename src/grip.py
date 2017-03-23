#!/usr/bin/python

import math
import sys
import os
import time

import cv2
import numpy

from point import P
import fdraw
import fits

import argparse

fitFuncs = {
    "gear": fits.bestPegFit,
    "goal": fits.bestGoalFit
}

parser = argparse.ArgumentParser(description='WOPR-JR Vision processing')
parser.add_argument('-mjpg', '--mjpg', default=None, type=int, help='do mjpg stream on what port')
parser.add_argument('-d', '--dir', default="./pics/", help='directory to store images')
parser.add_argument('-c', '--camera', type=int, default=0, help='camera port')
parser.add_argument('-show', '--show', action='store_true', help='show processed image')
parser.add_argument('-ni', '--noinfo', action='store_true', help='dont print the normal info')
parser.add_argument('-p', '--publish', action='store_true', help='publish to networktables')
parser.add_argument('-ip', '--address', type=str, default="roboRIO-3966-frc.local", help='network tables address')
parser.add_argument('-did', '--dashboardid', type=str, default="Center of ", help='smart dashboard publish ID')
parser.add_argument('-t', '--table', type=str, default="vision/gearpeg", help='smart dashboard publish ID')
parser.add_argument('-func', '--func', type=str, default="gear", help='smart dashboard publish ID')

parser.add_argument('-s', '--size', type=int, nargs=2, default=(320, 240), help='camera size')

parser.add_argument('-H', type=int, nargs=2, default=(0, 255), help='Hue')
parser.add_argument('-S', type=int, nargs=2, default=(0, 255), help='Saturation')
parser.add_argument('-L', type=int, nargs=2, default=(0, 255), help='Luminance')
parser.add_argument('-blur', type=int, nargs=2, default=(1, 1), help='Blur Size')
parser.add_argument('-exposure', type=float, default=1.0, help='Exposure')

parser.add_argument('-f', '--file', default="nothing.conf", help='config file')
args = parser.parse_args()


# sets our preferences
exec(open(args.file).read())

args.func = fitFuncs[args.func]


args.H = tuple(args.H)
args.S = tuple(args.S)
args.L = tuple(args.L)
args.blur = tuple(args.blur)

camera = None
im = None
retval = None

if args.publish:
    from networktables import NetworkTables
    NetworkTables.initialize(server=args.address)
    sd = NetworkTables.getTable("SmartDashboard")
    table = NetworkTables.getTable(args.table)

if args.mjpg:
    import stream
    stream.main("-c -1 -p {0} -d {1}".format(args.mjpg, args.dir).split())

def largestContours(contours, num=2):
    def keyFunc(contour):
        v = cv2.contourArea(contour)
        return v
    return sorted(contours, key=keyFunc, reverse=True)[0:num]

def process(source0):
    """
    Runs the pipeline and sets all outputs to new values.
    """
    source0 = cv2.blur(source0, args.blur)
    source0 = cv2.cvtColor(source0, cv2.COLOR_BGR2HLS)
    
    source0 = cv2.inRange(source0, (args.H[0], args.L[0], args.S[0]),  (args.H[1], args.L[1], args.S[1]))
    
    contours, hier = cv2.findContours(source0, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

    
    return contours

def set_exposure(ex):
    cmd = "v4l2-ctl -d /dev/video%d -c exposure_auto=1 -c exposure_absolute=%s" % (args.camera, str(ex))
    os.system(cmd)
    time.sleep(.125)

def init_camera():
    global camera
    
    set_exposure(args.exposure)
    
    camera = cv2.VideoCapture(args.camera)
    while camera is None:
        camera = cv2.VideoCapture(args.camera)

    #camera.set_exposure_auto(0)

    camera.set(3, args.size[0])
    camera.set(4, args.size[1])
#python src/grip.py -H 40 130 -S 40 255 -L 0 255 -blur 4 4 -exposure 100 -mjpg 8002 -c 1
num = 0
def get_image():
    global num
    global im
    global retval
    retval, im = camera.read()
    #im, retval = cv2.imread(".pics/highgoal/%d.png" % (num)), 1
    num += 1
    while im is None or not retval:
        time.sleep(.2)
        init_camera()
        retval, im = camera.read()
    return im

init_camera()
st, et = 0, 0
camst, camet = 0, 0

import time
pegFitness = 0

while True:
    st = time.time()
    camst = time.time()
    camera_capture=get_image()
    camet = time.time()

    fitness = float('inf')

    contours = process(camera_capture)
    if contours is None:
        contours = []

    center = P(-1, -1)

    if args.show or args.mjpg:
        fdraw.im = im

    try:
        if len(contours) >= 2:
            contours = [j for j in largestContours(contours, 4)]
            
            #contours, fitness = fits.bestPegFit(contours, args.size)
            contours, fitness = args.func(contours, args.size)

            if fitness < 10000:
                center = P(0, 0)
                for j in contours:
                    center = center + fits.contourCenter(j)
                
                center = (center / len(contours)).ints()
                

                if args.show or args.mjpg:
                    fdraw.contours(contours)
                    fdraw.powers(center, args.size)
                    fdraw.reticle(center, args.size)

        if args.show or args.mjpg:
            fdraw.axis(args.size)

    except Exception as e:
        print str(e)
    
    k = cv2.waitKey(1)
    et = time.time()
    
    fps = 1.0 / (et - st)
    camfps = 1.0 / (camet - camst)

    if fitness > 10000:
        fitness = 10000

    if args.mjpg: stream.im = im
    if args.show: cv2.imshow('img', im)

    if args.publish:
        #table = table.getSubTable(targetName)
        #if not sd.putString(args.dashboardid + targetName, str(center)):
		#    sd.delete(args.dashboardid)
		#    print ("Couldn't publish to smart dashboard\n")
					
        worked = True
        worked = worked and table.putNumber("fitness", fitness)

        worked = worked and table.putNumber("x", center.tuple()[0])
        worked = worked and table.putNumber("y", center.tuple()[1])
        
        worked = worked and table.putNumber("fps", fps)

        worked = worked and table.putNumber("camfps", camfps)
        worked = worked and table.putNumber("camwidth", args.size[0])
        worked = worked and table.putNumber("camheight", args.size[1])

        worked = worked and table.putNumber("time", time.time())

        if not worked:
            print ("Error while writing to table\n")

    if not args.noinfo:
        sys.stdout.write ("center: (%03d, %03d) fitness: %05d fps: %3.1f camfps: %.1f   \r" % (center.v[0], center.v[1], int(fitness), fps, camfps))
    sys.stdout.flush()
