#!/bin/bash
# Run this script to install the dependencies for Mousetrap on Fedora 21.

set -e

# Used with commands that may fail if we don't mind if they fail.
ignore_failure() {
	return 0
}


if [ ! -e README.md -o ! -e configure.ac ] ; then 
	echo "Please run from the project root"
	exit 1
fi

if [ ! -d vendor ] ; then
	mkdir vendor
fi

#python 3; yaml; gnome common; python3 setup-tools
sudo yum -y install cmake python3 python3-devel python3-numpy gcc gcc-c++ python3-PyYAML.x86_64 gnome-common python3-setuptools

#installation of numpy
sudo pip3 install numpy

#installation of x-lib python library
sudo rpm -ivh http://copr-be.cloud.fedoraproject.org/results/mosquito/myrepo/fedora-21-x86_64/python3-xlib-0.15git20141113-1.fc21/python3-xlib-0.15git20141113-1.fc21.noarch.rpm || ignore_failure

#install openCV 3
cd vendor
git clone --branch 3.0.0-beta --depth 1 https://github.com/Itseez/opencv.git
cd opencv
git checkout 3.0.0-beta

mkdir release
cd release

cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=$(python3 -c "import sys; print(sys.prefix)") -D PYTHON_EXECUTABLE=$(which python3) ..
make -j4
sudo make install


