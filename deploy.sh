#!/bin/bash

FROMDIR="$PWD"
FOLDER="WOPR-JR-Vision"
TMPDIR="/tmp/$FOLDER"

mkdir -p $TMPDIR

cd $TMPDIR

echo $TMPDIR
cp -R $FROMDIR/* ./
echo $TMPDIR

rm -rf .git
rm *.tar*

cd ..

echo "Tarring"
tar cfJ $FOLDER.tar.xz $FOLDER

cd $FROMDIR

cp $TMPDIR/../$FOLDER.tar.xz $FOLDER.tar.xz

TAR="$FOLDER.tar.xz"

TARGET="$1"
#SOURCES=./src/
SOURCES="WOPR-JR-Vision.tar.xz"

if [ "$TARGET" == "" ]; then
    TARGET="pi@raspberrypi.local"
fi
HERECMD="scp -r $SOURCES $TARGET:~/ ${@:2}"
EXECMD="cd ~; rm -rf WOPR-JR-Vision; tar xfv $TAR"

echo "Running here: $HERECMD"
bash -c "$HERECMD" || echo "Failed"

echo "Running on raspi: $EXECMD"
ssh $TARGET '$EXECMD' || echo "Failed"


