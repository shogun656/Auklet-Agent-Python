#!/usr/bin/env bash
set -e

echo "Creating files..."
mkdir -p .auklet

filelist="local.txt version communication usage limits"
for file in $filelist
do
    if [ ! -f .auklet/$file ]; then
        touch .auklet/$file
    fi
done

if [ ! -f key.pem ]; then
    touch key.pem
fi

if [ ! -f key.pem.zip ]; then
    zip key.pem.zip key.pem
fi

# This outputs the complete current python version to `pyver`
pyver=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')

if [[ "$pyver" < 3 ]]; then
    echo "Python2 detected..."
    COVERAGE_FILE=.coverage_python_2 coverage run --rcfile=".coveragerc" setup.py test
else
    echo "Python3 detected..."
    COVERAGE_FILE=.coverage_python_3 coverage run --rcfile=".coveragerc" setup.py test
fi

if [ -d .auklet ]; then
    rm -R .auklet
fi

if [ -f key.pem ]; then
    rm key.pem
fi

if [ -f key.pem.zip ]; then
    rm key.pem.zip
fi

