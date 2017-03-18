import math
import cv2

from point import P

def contourCenter(contour):
    try:
        mu = cv2.moments(contour, False) 
        return ( mu["m10"]/mu["m00"] , mu["m01"]/mu["m00"] )
    except:
        return (0, 0)

def bestPegFit(contours, size):
    min_indexes = (-1, -1)
    min_fitness = float('inf')
    def fitness(c1, c2, a1, a2):
        fromcenter = abs((2.0*c1[1]-size[1])/size[1])**2 + abs((2.0*c2[1]-size[1])/size[1])**2

        diff = (P(*c1)-c2).tuple()
        
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
        return 50*abs(diffangle) + 50*diffratio + 120*diffarea + 20*fromcenter
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
