
import cv2
from point import P

_rsize = 12
_rw = 2

offX = (_rsize, 0)
offY = (0, _rsize)

im = None

def contours(conts):
	cv2.drawContours(im, conts, 0, (150, 0, 150), _rw)
	cv2.drawContours(im, conts, 1, (150, 0, 150), 2*_rw)

def reticle(center, size):
	cc1 = (255, 0, 0)
	cc2 = (255, 200, 0)
	cv2.circle(im, center.tuple(), _rsize, cc1, _rw/2)
	cv2.line(im, (center - offX).tuple(), (center + offX).tuple(), cc1, _rw/2)
	cv2.line(im, (center - offY).tuple(), (center + offY).tuple(), cc1, _rw/2)
	base = P(center.tuple()[0], size[1]/2)
	cv2.circle(im, base.tuple(), _rsize, cc2, _rw)
	#cv2.line(im, (base - offX).tuple(), (base + offX).tuple(), (0, 0, 255), _rw)
	cv2.line(im, (base - offY).tuple(), (base + offY).tuple(), cc2, _rw)

def axis(size):
	cv2.line(im, (size[0] / 2, 0), (size[0] / 2, size[1]), (0, 0, 255), _rw)
	cv2.line(im, (0, size[1] / 2), (size[0], size[1] / 2), (0, 0, 255), _rw)

def powers(center, size):
	scl = (2.0*(center.tuple()[0]) - size[0]) / (2*size[0])
	if scl < 0:
		base = P(200, 120)
		cv2.rectangle(im, (base+(_rw, 0)).tuple(), (base + (20, scl*size[1])).ints().tuple(), (0, 255, 0), -1)
		base = P(120, 120)
		cv2.rectangle(im, (base+(_rw, 0)).tuple(), (base - (20, scl*size[1])).ints().tuple(), (255, 0, 0), -1)
	else:
		base = P(200, 120)
		cv2.rectangle(im, (base+(_rw, 0)).tuple(), (base + (20, scl*size[1])).ints().tuple(), (255, 0, 0), -1)
		base = P(120, 120)
		cv2.rectangle(im, (base+(_rw, 0)).tuple(), (base - (20, scl*size[1])).ints().tuple(), (0, 255, 0), -1)

