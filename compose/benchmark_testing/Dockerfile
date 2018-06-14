FROM python:3

ADD /compose/benchmark_testing/startBenchmarkTesting.sh /startBenchmarkTesting.sh
ADD /compose/benchmark_testing/src /src
ADD ./auklet /auklet
ADD / /


RUN mkdir .auklet

RUN apt-get update && apt-get install -y netcat

RUN pip3 install \
    pidigits \
    six \
    kafka \
    ipify \
    mock

RUN python3 /setup.py install