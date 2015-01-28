#!/bin/bash
set -x

if [ -n "$LINT" ]
then
    bin/lint.bash
else
    bin/ci-test.bash
fi
