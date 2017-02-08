
import socket, pickle
import sys

host = "10.39.66.177"
port = 23

# enough for 2 colors, 2 args, and a function
NUM_ARGS = (1) + (2*3+2)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host, port))

byte_send = map(int, sys.argv[1:])

if len(byte_send) > NUM_ARGS:
	print ("ERROR: you entered more bytes than expected (expected {0}, got {1})".format(NUM_ARGS, len(byte_send)))
	byte_send = byte_send[0:NUM_ARGS]

if len(byte_send) < NUM_ARGS:
	print ("ERROR: you entere less bytes than expected (expected {0}, got {1})".format(NUM_ARGS, len(byte_send)))
	byte_send = byte_send + [0]*(NUM_ARGS-len(byte_send))

print ("Sending bytes:\n{0}".format(byte_send))

s.send(bytearray(byte_send))

s.close()

