#!/usr/bin/env bash

while ! nc -z mqtt 1883; do
  sleep 1
done

mkdir .auklet
if [[ "$CIRCLECI" == "true" ]]; then
  sudo python3 setup.py install
else
  python3 /setup.py install
fi
python3 src/benchmark/run_tests.py
