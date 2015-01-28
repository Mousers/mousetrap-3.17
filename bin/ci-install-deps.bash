#!/bin/bash
set -x

if [ -n "$LINT" ]
then
    pip install flake8
    pip install coverage
fi

# Python file locations
PYTHON_VERSION=$(python -c "import sys; print('%s.%s' % sys.version_info[:2])")
PYTHON_INC_DIR=$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")
PYTHON_SITE_PACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

if [ -n "$OPENCV_VERSION" ]
then
    # Update CMake to 2.8.12
    sudo add-apt-repository --yes ppa:kalakris/cmake
    sudo apt-get update -qq
    sudo apt-get install cmake

    # Basic dependencies
    sudo apt-get install gnome-common libopencv-dev
    pip install pyyaml

    # PyGI dependency
    if [ $PYTHON_VERSION == "2.7" ];
    then
        sudo apt-get install python-gi
        PYGI_LOCATION=$(dpkg-query -L python-gi | grep "packages/gi$")
    else
        sudo apt-get install python3-gi
        PYGI_LOCATION=$(dpkg-query -L python3-gi | grep "packages/gi$")
    fi

    # Link it to work in the virtualenv
    ln -s $PYGI_LOCATION "${PYTHON_SITE_PACKAGES}/gi"

    # Xlib dependency
    if [ $PYTHON_VERSION == "2.7" ]
    then
        sudo apt-get install python-xlib
        XLIB_LOCATION=$(dpkg-query -L python-xlib | grep "/Xlib$")
        ln -s $XLIB_LOCATION "${PYTHON_SITE_PACKAGES}/Xlib"
    else
        pip install python3-xlib
    fi

    # OpenCV build variables
    OPENCV_PYTHON_INCLUDE="PYTHON_INCLUDE_DIR"
    OPENCV_PYTHON_PACKAGES="PYTHON2_PACKAGES_PATH"

    # OpenCV 2 overrides
    if [ $OPENCV_VERSION == "2.4.10.1" ]
    then
        OPENCV_PYTHON_PACKAGES="PYTHON_PACKAGES_PATH"
    fi

    # OpenCV download
    git clone --single-branch --branch $OPENCV_VERSION https://github.com/Itseez/opencv.git ~/opencv-3
    cd ~/opencv-3
    mkdir release
    cd release

    # OpenCV buld and install
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
          -D BUILD_opencv_java=OFF \
          -D PYTHON_EXECUTABLE=$(which python) \
          -D ${OPENCV_PYTHON_INCLUDE}=$PYTHON_INC_DIR \
          -D ${OPENCV_PYTHON_PACKAGES}=$PYTHON_SITE_PACKAGES ..
    make
    sudo make install
fi
