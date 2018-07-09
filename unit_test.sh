#!/usr/bin/env bash

if [ ! -d .auklet ]; then
    mkdir .auklet
    touch .auklet/local.txt
    touch .auklet/version
fi

testmodules=("monitoring/test___init__" "monitoring/test_logging" "monitoring/test_sampling" "test_base" "test_errors" "test_stats")

for name in "${testmodules[@]}"; do
    python3 "tests/$name.py"
done

rm -R .auklet