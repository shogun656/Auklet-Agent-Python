FROM python:3

RUN apt-get update && apt-get install -y netcat

COPY ./compose/benchmark/startBenchmark.sh /startBenchmark.sh
COPY ./setup.py /setup.py
COPY ./requirements.txt /requirements.txt
COPY ./requirements.testing.txt /tests/requirements.txt

RUN pip install -r /requirements.txt
RUN pip install -r /tests/requirements.txt

# Set working dir to app root for running commands.
WORKDIR /app