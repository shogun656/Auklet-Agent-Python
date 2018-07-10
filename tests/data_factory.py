import random
import string
import factory

from time import time


def chars(n):
    return ''.join(random.choices("abcdef" + string.digits, k=n))


class MonitoringDataGenerator(object):
    def __init__(self, commitHash, id, publicIP, timestamp, application,
                 macAddressHash, lineNumber, nSamples, functionName, nCalls):
        self.commitHash = commitHash
        self.id = id
        self.publicIP = publicIP
        self.timestamp = timestamp
        self.application = application
        self.macAddressHash = macAddressHash

        self.lineNumber = lineNumber
        self.nSamples = nSamples
        self.functionName = functionName
        self.nCalls = nCalls

    def __str__(self):
        return '{"commitHash": "%s", ' \
               '"id": "%s", ' \
               '"publicIP": "%s", ' \
               '"timestamp": %d, ' \
               '"application": "%s", ' \
               '"macAddressHash": "%s", ' \
               '"callees": [{"lineNumber": %d, "nSamples": %d, "functionName": "%s", "nCalls": %d}]}' \
               % (self.commitHash, self.id, self.publicIP, self.timestamp, self.application,
                  self.macAddressHash, self.lineNumber, self.nSamples, self.functionName, self.nCalls)


class MonitoringDataFactory(factory.Factory):

    class Meta:
        model = MonitoringDataGenerator

    commitHash = chars(40)
    id = str(chars(8) + '-' + chars(4) + '-' + chars(4) + '-' + chars(12))
    publicIP = '.'.join(map(str, (random.randint(0, 255) for _ in range(4))))
    timestamp = int(round(time() * 1000))
    application = ''.join(random.choices(string.ascii_letters, k=22))
    macAddressHash = chars(32)
    lineNumber = int(random.randint(0, 1000))
    nSamples = int(random.randint(1000, 10000))
    functionName = "root"
    nCalls = 0


class ConfigGenerator(object):
    def __init__(self, brokers, prof_topic, event_topic, log_topic, user_metrics_topic):
        self.brokers = brokers
        self.prof_topic = prof_topic
        self.event_topic = event_topic
        self.log_topic = log_topic
        self.user_metrics_topic = user_metrics_topic

    def __str__(self):
        return '{"brokers": ["%s"], "prof_topic": "%s", "event_topic": ' \
               '"%s", "log_topic": "%s", "user_metrics_topic": "%s"}' \
                % (self.brokers, self.prof_topic, self.event_topic, self.log_topic, self.user_metrics_topic)


class ConfigFactory(factory.Factory):

    class Meta:
        model = ConfigGenerator

    brokers = "brokers-staging.feeds.auklet.io:9093"
    prof_topic = "profiler"
    event_topic = "events"
    log_topic = "logs"
    user_metrics_topic = "user_metrics"
