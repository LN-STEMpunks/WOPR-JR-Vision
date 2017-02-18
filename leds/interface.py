
import socket
import pickle
import sys

import time

import argparse

parser = argparse.ArgumentParser(description='WOPR-JR LED interface')


parser.add_argument('-b', '--bytes', type=str, nargs='*', default=[], help='bytes to send')
parser.add_argument('-ip', '--address', type=str, default="roboRIO-3966-frc.local", help='network tables address')
parser.add_argument('-arduinoip', '--arduinoaddress', type=str, default="10.39.66.177:23", help='arduino address')
parser.add_argument('-t', '--table', type=str, default="vision/gearpeg", help='networktables table')
parser.add_argument('-n', '--numbytes', type=int, default=(4 * 3 + 4), help='number of bytes expected')

args = parser.parse_args()

time.sleep(args.delay)

host = args.arduinoaddress.split(":")[0]
port = int(args.arduinoaddress.split(":")[1])

# enough for 4 colors, 4 args, and a function
NUM_ARGS = (4 * 3 + 4) + 1
s = None
while s is None:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    except:
        s.close()
        s = None
        time.sleep(1.0)

CYLON_FUNC_ID = "17"
COLOR_BAR = "0,255,0"
COLOR_BACKGROUND = "255,0,0"
# here goes width
FADE = "0"
DELAY = "10"

MAX_WIDTH = 150


def sendbytes(byte_send):
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.connect((host, port))
    byte_send = ",".join(byte_send).split(",")
    byte_send = map(int, byte_send)

    if len(byte_send) > NUM_ARGS:
        #print ("ERROR: you entered more bytes than expected (expected {0}, got {1})".format(NUM_ARGS, len(byte_send)))
        byte_send = byte_send[0:NUM_ARGS]

    if len(byte_send) < NUM_ARGS:
        #print ("ERROR: you entered less bytes than expected (expected {0}, got {1})".format(NUM_ARGS, len(byte_send)))
        byte_send = byte_send + [0] * (NUM_ARGS - len(byte_send))

    s.send(bytearray(byte_send))
    # s.close()
    return bytearray(byte_send)

if len(args.bytes) > 0:
    # so you can enter , s
    print (sendbytes(args.bytes))

else:
    from networktables import NetworkTables
    NetworkTables.initialize(server=args.address)
    table = NetworkTables.getTable(args.table)

    time.sleep(.5)

    def fitness_to_width(fit):
        if fit <= MAX_WIDTH:
            return MAX_WIDTH
        ret = int(MAX_WIDTH * (50.0 / (fit)))
        if ret > 255:
            ret = 255
        return ret

    def x_to_width(camw, _x):
        if _x < 0:
            return 0
        return MAX_WIDTH - 1.6 * MAX_WIDTH * (abs(2 * _x - camw) / camw)

    while True:
        try:
            fitness = table.getNumber("fitness")
            x = table.getNumber("x")
            cw = table.getNumber("camwidth")
            width = x_to_width(cw, x)
            print width
            sendbytes(["18,0,255,0", str(int(width))])
            #sendbytes(["18", "0", "255", "0", str(int(width)), DELAY])
            s.close()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
        except:
            s.close()
            time.sleep(.25)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
        time.sleep(.1)
