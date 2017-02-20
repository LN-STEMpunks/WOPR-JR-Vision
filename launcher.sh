#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

export VISIONREPO=/home/pi/WOPR-JR-Vision

# Camera 0, and 1
/usr/bin/env python ${VISIONREPO}/src/grip.py -f ${VISIONREPO}/comp.conf --publish -c 0 &
/usr/bin/env python ${VISIONREPO}/src/grip.py -f ${VISIONREPO}/comp.conf --publish -c 1 &

/usr/bin/env python ${VISIONREPO}/leds/interface.py &

exit 0


