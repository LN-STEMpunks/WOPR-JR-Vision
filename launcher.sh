#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

export VISIONREPO=/home/pi/WOPR-JR-Vision

# Camera 0, and 1
#/usr/bin/env python ${VISIONREPO}/src/grip.py -c 0 -t vision/gearpeg -f ${VISIONREPO}/ohio-gearpeg.conf  -mjpg 8000 --publish &
#/usr/bin/env python ${VISIONREPO}/src/grip.py -c 1 -t vision/highgoal -f ${VISIONREPO}/ohio-highgoal.conf  -mjpg 8001 --publish &

#Use this for serial connection to arduino UNO
#/usr/bin/env python ${VISIONREPO}/leds/interface.py --serial /dev/ttyACM0 &

#Use this for ethernet connection to arduino Ethernet
#/usr/bin/env python ${VISIONREPO}/leds/interface.py &

/usr/bin/env python ${VISIONREPO}/src/lidar.py --publish &

exit 0


