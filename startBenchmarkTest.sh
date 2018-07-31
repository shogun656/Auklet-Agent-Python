#!/bin/bash

docker-compose down
docker-compose build
docker-compose run benchmark bash /startBenchmark.sh