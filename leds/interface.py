import serial
ser = serial.Serial('/dev/ttyUSB5', 9600)

import time
import sys

#ser.write("2,255,255,0,200,0;")
#ser.write(str(sys.argv[1])

ser.write(bytearray([int(sys.argv[1])]))


#for i in range(1, 150):
	#ser.write("3,0,0,0,%s;" % (i-1))
	#ser.write("0,255,255,255,%s;" % (i))
	#time.sleep(.04)

#ser.write(sys.argv[1])
#ser.write("2,255,1,1,0;")

ser.close()
