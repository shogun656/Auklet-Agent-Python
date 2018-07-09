#!/usr/bin/env bash

if [ ! -d .auklet ]; then
    mkdir .auklet
    touch .auklet/local.txt
    touch .auklet/version
fi

pyenv install 3.6.3
pyenv global 3.6.3

pip3 install mock kafka

python3 setup.py install

for file in "tests/monitoring/test___init__.py" "tests/monitoring/test_logging.py" "tests/monitoring/test_sampling.py" "tests/test_base.py" "tests/test_errors.py" "tests/test_stats.py"
do
    python3 $file
done

rm -R .auklet