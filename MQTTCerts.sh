#!/bin/bash
set -e
echo 'Getting MQTT certs'
CERTFILE="./certs-$RANDOM.zip"
aws --region us-east-1 s3 cp s3://$CERTS_S3_BUCKET/$CERTS_S3_KEY $CERTFILE
unzip -q -o $CERTFILE -d $(dirname $CERTFILE)
