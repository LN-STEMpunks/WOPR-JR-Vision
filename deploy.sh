#!/bin/bash

TARGET="$1"
#SOURCES=./src/
SOURCES="WOPR-JR-Vision.tar.xz"

if [ "$TARGET" == "" ]; then
    TARGET="pi@raspberrypi.local:~/"
fi
CMD="scp -r $SOURCES $TARGET ${@:2}"

echo "$CMD"
bash -c "$CMD" || echo "Failed"
