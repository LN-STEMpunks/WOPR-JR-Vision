#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

export VISIONREPO=/home/pi/WOPR-JR-Vision

# Camera 0, and 1
/usr/bin/env python ${VISIONREPO}/src/grip.py -mjpg 5801 -f ${VISIONREPO}/lab.conf --publish -c 0 &
/usr/bin/env python ${VISIONREPO}/src/grip.py -f ${VISIONREPO}/lab.conf --publish -c 1 &

#Use this for serial connection to arduino UNO
#/usr/bin/env python ${VISIONREPO}/leds/interface.py --serial /dev/ttyACM0 &

#Use this for ethernet connection to arduino Ethernet
/usr/bin/env python ${VISIONREPO}/leds/interface.py &

/usr/bin/env python ${VISIONREPO}/src/lidar.py --publish &

exit 0


