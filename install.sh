#!/bin/bash

if [ "$UID" -ne "0" ]; then
    printf "ERROR: must be root\n"
    sudo $0
    exit $?
fi

apt install python-pip
apt install libopencv-dev
apt install python-opencv

