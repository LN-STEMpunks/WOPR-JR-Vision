
import socket, pickle
import sys


import argparse

parser = argparse.ArgumentParser(description='WOPR-JR LED interface')

parser.add_argument('bytes', metavar='bytes', type=str, nargs='*', default=[], help='bytes to send')

args = parser.parse_args()

host = "10.39.66.177"
port = 23

# enough for 4 colors, 4 args, and a function
NUM_ARGS = (4*3+4)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host, port))

# so you can enter , s
byte_send = ",".join(sys.argv[1:]).split(",")
byte_send = map(int, byte_send)

if len(byte_send) > NUM_ARGS:
	print ("ERROR: you entered more bytes than expected (expected {0}, got {1})".format(NUM_ARGS, len(byte_send)))
	byte_send = byte_send[0:NUM_ARGS]

if len(byte_send) < NUM_ARGS:
	print ("ERROR: you entere less bytes than expected (expected {0}, got {1})".format(NUM_ARGS, len(byte_send)))
	byte_send = byte_send + [0]*(NUM_ARGS-len(byte_send))

print ("Sending bytes:\n{0}".format(byte_send))

s.send(bytearray(byte_send))

s.close()

