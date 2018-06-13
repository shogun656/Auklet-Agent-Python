FROM python:3

ADD /compose/benchmark_testing/src /src

ADD ./auklet /auklet

RUN mkdir .auklet

RUN pip3 install \
    pidigits \
    six \
    kafka \
    ipify