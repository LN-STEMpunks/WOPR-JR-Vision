# for testing 
import serial
import time
from random import randint

NUM_ARGS = (4 * 3 + 4) + 1
#ser = serial.Serial('COM7', 38400, timeout=1)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

#give the arduino time to wake up
time.sleep(2)

# r = randint(0,255);
# g = randint(0,255);
# b = randint(0,255);
r = 255
g = 0
b = 0
counter = 0
# while True and counter < 1:
while True :
    #ser.write("!2,255,0,0$")
    cmd = "A2," + `r` + "," + `g` + "," + `b` + "Z"
    print (cmd)
    ser.write(cmd)
    print ser.readline()
    # r = (r+1)%255
    # g = (g+1)%255
    # b = (b+1)%255
    # r = randint(0,255);
    # g = randint(0,255);
    # b = randint(0,255);
    if r == 255:
        r = 0
        g = 255
        b = 0
    elif g == 255:
        r = 0
        g = 0
        b = 255
    else:
        r = 255
        g = 0
        b = 0
    counter +=1
    time.sleep(.01)

#time.sleep(1)