#!/bin/bash

if [ "$UID" -ne "0" ]; then
    printf "ERROR: must be root\n"
    sudo $0
    exit $?
fi

apt install libopencv-dev
apt install python-opencv
apt install v4l-utils
#apt install python-pip
#pip install flask

# todo test
yum install numpy "opencv*"

