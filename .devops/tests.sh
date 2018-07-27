#!/usr/bin/env bash
set -e

echo "Creating files..."
mkdir -p .auklet
mkdir -p .coverage_files

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
echo $pyver
COVERAGE_FILE=.coverage.python${pyver} coverage run --rcfile=".coveragerc" setup.py test

if [ -d .auklet ]; then
    rm -R .auklet
fi

if [ -f key.pem ]; then
    rm key.pem
fi

if [ -f key.pem.zip ]; then
    rm key.pem.zip
fi

