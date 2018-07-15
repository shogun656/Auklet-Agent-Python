#!/usr/bin/env bash
set -e

if [ ! -d .auklet ]; then
    mkdir .auklet
    touch .auklet/local.txt
    touch .auklet/version
fi

coverage run --rcfile=".coveragerc" setup.py test
coverage html -d htmlcov
coverage xml

rm -R .auklet