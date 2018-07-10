#!/usr/bin/env bash

if [ ! -d .auklet ]; then
    mkdir .auklet
    touch .auklet/local.txt
    touch .auklet/version
fi

coverage run --source="auklet" setup.py test

rm -R .auklet