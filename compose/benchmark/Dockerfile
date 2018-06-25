FROM python:3

ADD ./compose/benchmark/startBenchmark.sh /startBenchmark.sh
ADD ./setup.py /setup.py
ADD ./requirements.txt /requirements.txt

RUN mkdir .auklet

RUN apt-get update && apt-get install -y netcat

RUN pip install -r /requirements.txt

RUN python3 /setup.py install