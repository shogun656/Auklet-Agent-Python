#!/bin/bash
set -e
cd ~

echo 'Installing Oracle JRE 8...'
JAVA_HOME='jre'
mkdir $JAVA_HOME
curl -jLs -H "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jre-8u131-linux-x64.tar.gz | tar -C $JAVA_HOME --strip-components=1 -xz

# Download pip packages into a new directory for scanning.
# Use the requirements file defined in the Dockerfile so we pull the correct packages.
# We can't use the pip cache because results are not nearly as accurate.
echo 'Downloading pip packages for WhiteSource analysis...'
PACKAGES_DIR='.whitesource-pip'
pip download -r app/requirements.txt -d $PACKAGES_DIR

WS_AGENT_URL='https://s3.amazonaws.com/file-system-agent/whitesource-fs-agent-1.8.0.jar'
WS_AGENT='whitesource.jar'
curl -Ls $WS_AGENT_URL > $WS_AGENT

WS_CONFIG_SRC='app/whitesource.cfg'
WS_CONFIG='whitesource-final.cfg'
cp $WS_CONFIG_SRC $WS_CONFIG
echo "apiKey=$WHITESOURCE_ORG_TOKEN" >> $WS_CONFIG
echo "productToken=$WHITESOURCE_PRODUCT_TOKEN" >> $WS_CONFIG
VERSION=$(cat ~/.version)
echo "projectVersion=$VERSION" >> $WS_CONFIG

echo 'Starting WhiteSource File System Agent...'
$JAVA_HOME/bin/java -jar $WS_AGENT -c $WS_CONFIG -d $PACKAGES_DIR
RESULT=$?
# TODO
# Add failure logic where applicable.
# Success=0, Error=-1, Policy Violation=-2, Client Failure=-3, Connection Failure=-4

rm -rf $JAVA_HOME
rm $WS_AGENT
rm $WS_CONFIG