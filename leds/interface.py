import socket
import pickle
import sys
import serial
import time
import argparse

parser = argparse.ArgumentParser(description='WOPR-JR LED interface')


parser.add_argument('-b', '--bytes', type=str, nargs='*', default=[], help='bytes to send')
parser.add_argument('-ip', '--address', type=str, default="roboRIO-3966-frc.local", help='network tables address')
parser.add_argument('-aip', '--arduinoaddress', type=str, default="10.39.66.177:5800", help='arduino address')
parser.add_argument('-t', '--table', type=str, default="vision", help='networktables table')
parser.add_argument('-n', '--numbytes', type=int, default=(4 * 3 + 4), help='number of bytes expected')
parser.add_argument('-s', '--serial', type=str, help='serial port to arduino')
parser.add_argument('-baud', '--baud', type=int, default=38400, help='serial baud')

args = parser.parse_args()

RED="150,0,0"
BLUE="0,0,150"

def getColorFromEnum(enum):
	enum = int(enum)
	if enum == 0:
		return RED
	elif enum == 1:
		return BLUE
	else:
		return "50, 50, 500"

host = args.arduinoaddress.split(":")[0]
port = int(args.arduinoaddress.split(":")[1])

# enough for 4 colors, 4 args, and a function
NUM_ARGS = (4 * 3 + 4) + 1

s = None

def connect():
    global s
    if args.serial :
        print "connecting serial", args.serial, args.baud
        s = serial.Serial(args.serial, args.baud, timeout=1)
        #give the arduino time to wake up
        time.sleep(2)
    else :
        print "connecting ethernet"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

def close():
    if s :
        s.close()
        
while s is None:
    try:
        connect()
    except Exception as e: 
        print str(e)
        print 'exception in opening, waiting for retry'
        close()
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
    if args.serial :
        byte_send = ",".join(byte_send)
        # serial protocol uses the A to start and Z to end the packets. add them if not already there
        if byte_send.startswith("A") == False:
            byte_send = "A" + byte_send
        if byte_send.endswith("Z") == False:
            byte_send = byte_send + "Z"
        s.write(byte_send)
        # we call readline() because arduino seems to overrun its buffer if you don't read from it sometimes
        s.readline()
    else:  
        byte_send = ",".join(byte_send).split(",")
        byte_send = map(int, byte_send)

        if len(byte_send) > NUM_ARGS:
            #print ("ERROR: you entered more bytes than expected (expected {0}, got {1})".format(NUM_ARGS, len(byte_send)))
            byte_send = byte_send[0:NUM_ARGS]

        if len(byte_send) < NUM_ARGS:
            #print ("ERROR: you entered less bytes than expected (expected {0}, got {1})".format(NUM_ARGS, len(byte_send)))
            byte_send = byte_send + [0] * (NUM_ARGS - len(byte_send))

        s.send(bytearray(byte_send))
    return bytearray(byte_send)

if len(args.bytes) > 0:
    # so you can enter , s
    print (sendbytes(args.bytes))

else:
    from networktables import NetworkTables
    NetworkTables.initialize(server=args.address)
    table = NetworkTables.getTable(args.table)
    infotable = NetworkTables.getTable("info")
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
            goalTime = table.getSubtable("highgoal").getNumber("time")
            pegTime = table.getSubtable("gearpeg").getNumber("time")
            stable = table
            if goalTime > pegTime:
                stable = table.getTable("highgoal")
            else:
                stable = table.getTable("gearpeg")
            x = stable.getNumber("x")
            cw = stable.getNumber("camwidth")
            width = x_to_width(cw, x)
            print width
            #sendbytes(["18,0,255,0", str(int(width))])
            sendbytes(["19", getColorFromEnum(infotable.getNumber("color"), "100,0,100", int(width))])
            #sendbytes(["18", "0", "255", "0", str(int(width)), DELAY])
            if args.serial:
                time.sleep(0.001)
            else:
                close()
                connect()
        except:
            close()
            time.sleep(.25)
            connect()
        time.sleep(.1)
