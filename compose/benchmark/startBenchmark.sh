#!/usr/bin/env bash

while ! nc -z mqtt 1883; do
  sleep 1
done

mkdir .auklet
python3 /setup.py install
python3 src/benchmark/run_tests.py