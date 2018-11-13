#!/usr/bin/env bash
set -e

echo "Creating files..."
mkdir -p .auklet

filelist="local.txt version communication usage limits"
for file in $filelist
do
    touch .auklet/$file
done

touch key.pem
zip key.pem.zip key.pem

# This outputs the complete current python version to `pyver`
pyver=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
echo Python $pyver

COVERAGE_FILE=.coverage.python$pyver coverage run --rcfile=".coveragerc" setup.py test

rm -Rf .auklet
rm -f key.pem
rm -f key.pem.zip