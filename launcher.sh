#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

export VISIONREPO=/home/pi/WOPR-JR-Vision

/usr/bin/env python ${VISIONREPO}/src/grip.py -f ${VISIONREPO}/lab.conf --publish &

/usr/bin/env python ${VISIONREPO}/leds/interface.py &

exit 0


