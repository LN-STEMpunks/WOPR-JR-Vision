#!/bin/sh

FROMDIR="$PWD"
FOLDER="WOPR-JR-Vision"
TMPDIR="/tmp/$FOLDER"


mkdir -p $TMPDIR

cd $TMPDIR

cp -Rf $FROMDIR/* ./

rm -rf .git
rm *.tar*

cd ..

tar cfJ $FOLDER.tar.xz $FOLDER

cd $FROMDIR

cp $TMPDIR/../$FOLDER.tar.xz $FOLDER.tar.xz


