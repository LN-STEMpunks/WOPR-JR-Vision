
import socket, pickle
import sys

host = "10.39.66.177"
port = 23

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host, port))

byte_send = map(int, sys.argv[1:])

print byte_send

s.send(bytearray(byte_send))

s.close()

