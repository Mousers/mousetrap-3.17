#!/bin/bash
set -x

if [ -n "$OPENCV_VERSION" ]
then
    ./autogen.sh && make
fi
