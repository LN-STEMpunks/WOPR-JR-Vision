#!/bin/bash

if [ "$UID" -ne "0" ]; then
    printf "ERROR: must be root\n"
    sudo $0
    exit $?
fi

apt install libopencv-dev python-opencv v4l-utils python-imaging

# todo test for redhat/fedora systems
# yum install numpy "opencv*"

