#!/bin/bash

docker-compose down
docker-compose build
# docker-compose run benchmark bash /compose/benchmark/startBenchmark.sh
docker-compose up
