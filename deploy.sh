#!/bin/bash

TARGET="$1"
SOURCES=./src/

if [ "$TARGET" == "" ]; then
    TARGET="pi@raspberrypi.local:~/Documents/"
fi
CMD="scp -r $SOURCES $TARGET ${@:2}"

echo "$CMD"
bash -c "$CMD" || echo "Failed"
