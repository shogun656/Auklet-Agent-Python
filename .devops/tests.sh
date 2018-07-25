#!/usr/bin/env bash
set -e

if [ ! -d .auklet ]; then
    mkdir .auklet
    touch .auklet/local.txt
    touch .auklet/version
fi

if [ -d htmlcov ]; then
    rm -R htmlcov
fi

coverage run --rcfile=".coveragerc" setup.py test
coverage report -m
coverage html -d tmp/htmlcov
coverage xml

if [ -d .auklet ]; then
    rm -R .auklet
fi