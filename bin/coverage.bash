#!/bin/bash
if [ -e .coverage ] ; then
    coverage report -m
else
    echo "bin/coverage.bash: .coverage file not found. Skipping coverage report."
fi
