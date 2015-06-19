#!/bin/bash
# Run this to generate all the initial makefiles, etc.


## Guess the python version to use. Defaults to Python 2.7
## To make python3 the default, move python3 to the front of
## python_search_order.
python_search_order="python python3"
for python_version in $python_search_order ; do
    if [ -z "$PYTHON" ] ; then
        PYTHON="$(which $python_version)"
    fi
done
export PYTHON

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

PKG_NAME="MouseTrap"

(test -f $srcdir/configure.ac \
  && test -f $srcdir/README.md \
  && test -d $srcdir/src) || {
    echo -n "**Error**: Directory "\`$srcdir\'" does not look like the"
    echo " top-level $PKG_NAME directory"
    exit 1
}

which gnome-autogen.sh || {
    echo "You need to install gnome-common from the GNOME CVS"
    exit 1
}

REQUIRED_AUTOMAKE_VERSION=1.9

USE_GNOME2_MACROS=1 USE_COMMON_DOC_BUILD=yes . gnome-autogen.sh
