import serial
ser = serial.Serial('/dev/ttyUSB1', 9600)

#ser.write(bytearray([int(sys.argv[1])]))
import time

for i in range(1, 150):
	ser.write("3,0,0,0,%s;" % (i-1))
	ser.write("3,255,255,255,%s;" % (i))
	time.sleep(.04)

#ser.write(sys.argv[1])
#ser.write("2,255,1,1,0;")

ser.close()
