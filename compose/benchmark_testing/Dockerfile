FROM python:3

ADD /compose/benchmark_testing/src /src

ADD ./.auklet /.auklet
ADD ./auklet /auklet

RUN pip3 install \
    pidigits \
    six \
    kafka \
    ipify

#RUN apt-get update && apt-get install -y vim netcat-openbsd