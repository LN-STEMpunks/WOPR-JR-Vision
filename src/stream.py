import threading

import time
import sys
import os
import argparse

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import StringIO
import Image

import cv2

im = None

class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		global im
		self.send_response(200)
		self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
		self.end_headers()
		while True:
			try:
				jpg = Image.fromarray(im)
				tmpFile = StringIO.StringIO()
				jpg.save(tmpFile,'JPEG')
				self.wfile.write("--jpgboundary")
				self.send_header('Content-type','image/jpeg')
				self.send_header('Content-length',str(tmpFile.len))
				self.end_headers()
				jpg.save(self.wfile, 'JPEG')
				time.sleep(0.05)
			except KeyboardInterrupt:
				break
		return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def do_camera_update(cam, fps, place, max, every):
	global im
	num = 0
	ct = 0
	while True:
		try:
			retval, im = cam.read()
			if ct % every == 0 and num < max:
				cv2.imwrite('{0}/{1}.png'.format(place, num), im)
				num += 1
			ct += 1
			time.sleep(1.0 / fps)
		except KeyboardInterrupt:
			break

def main(opts):
	parser = argparse.ArgumentParser(description='WOPR-JR Vision processing')
	parser.add_argument('-c', '--camera', type=int, default=0, help='camera port')
	parser.add_argument('-fps', '--fps', type=float, default=12.0, help='camera port')
	parser.add_argument('-p', '--port', type=int, default=8001, help='port to publish on')
	parser.add_argument('-d', '--dir', type=str, default=None, help='directory to store pics')
	parser.add_argument('-max', type=int, default=2000, help='only store N frames alltogether')
	parser.add_argument('-every', type=int, default=3, help='store 1 in N frames')

	#parser.add_argument('-path', '--path', default="nothing.conf", help='config file')
	args = parser.parse_args(opts)

	#im = None

	server = ThreadedHTTPServer(('0.0.0.0', args.port), CamHandler)

	print "server started"
	pthread = threading.Thread(target=server.serve_forever)
	pthread.start()
	
	if args.camera >= 0:
		camera = cv2.VideoCapture(args.camera)
		do_camera_update(camera, args.fps, args.dir, args.max, args.every)

if __name__ == "__main__":
	exit(main(sys.argv[1:]))
