FROM nimmis/java:14.04-openjdk-8-jre-headless
USER root
ENV DEBIAN_FRONTEND noninteractive

# Install AWS CLI and zip
RUN apt-get update && apt-get install -y awscli zip

# Install Kafka.
RUN mkdir kafka ; wget https://archive.apache.org/dist/kafka/0.11.0.0/kafka_2.11-0.11.0.0.tgz -q -O - | tar -C kafka --strip-components=1 -xvz

# Enable Kafka topic deletion.
RUN sed -i "s/^#delete.topic.enable=true/delete.topic.enable=true/" ./kafka/config/server.properties

# Configure listeners.
RUN sed -i "s/^#advertised.listeners=PLAINTEXT:\/\/your.host.name:9092/advertised.listeners=PLAINTEXT:\/\/kafka:9092/" ./kafka/config/server.properties
RUN sed -i "s/^#listeners=PLAINTEXT:\/\/:9092/listeners=PLAINTEXT:\/\/:9092/" ./kafka/config/server.properties

# Copy startup script.
COPY ./compose/kafka/startKafka.sh /startKafka.sh

# Store kafka logs in a volume (better "tail -f" support).
RUN mkdir kafka/log
VOLUME /root/kafka/log

# Set Ubuntu's timezone.
RUN set_tz America/Detroit