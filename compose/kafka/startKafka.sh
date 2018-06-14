#!/bin/sh

set -e

echo 'Starting Zookeeper...'
nohup ./kafka/bin/zookeeper-server-start.sh ./kafka/config/zookeeper.properties > ./kafka/log/zookeeper.log 2>&1 &
while ! nc -z localhost 2181; do
  sleep 1
done

echo 'Starting Kafka...'
nohup ./kafka/bin/kafka-server-start.sh ./kafka/config/server.properties > ./kafka/log/kafka.log 2>&1 &
while ! nc -z localhost 9092; do
  sleep 1
done

echo 'Creating Kafka topic...'
./kafka/bin/kafka-topics.sh --create --if-not-exists --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic profiling
./kafka/bin/kafka-topics.sh --create --if-not-exists --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic events
./kafka/bin/kafka-topics.sh --create --if-not-exists --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic logging

tail -f /dev/null