#!/bin/bash

if [ "$UID" -ne "0" ]; then
    printf "ERROR: must be root\n"
    sudo $0
    exit $?
fi

apt install libopencv-dev
apt install python-opencv

# todo test
yum install numpy "opencv*"

