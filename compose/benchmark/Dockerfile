FROM python:3

ADD ./compose/benchmark/startBenchmark.sh /compose/benchmark/startBenchmark.sh
ADD ./src /src
ADD ./auklet /auklet
ADD ./setup.py /setup.py
ADD ./setup.cfg /setup.cfg
ADD ./README.md /README.md
ADD ./requirements.txt /requirements.txt
ADD ./test_requirements.txt /test_requirements.txt

RUN mkdir .auklet

RUN apt-get update && apt-get install -y netcat

RUN pip install -r /requirements.txt

RUN python3 /setup.py install
