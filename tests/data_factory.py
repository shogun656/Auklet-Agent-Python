import factory


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
               '"callees": ' \
               '[{"lineNumber": %d, ' \
               '"nSamples": %d, ' \
               '"functionName": "%s", ' \
               '"nCalls": %d}]}' \
               % (self.commitHash, self.id, self.publicIP,
                  self.timestamp, self.application, self.macAddressHash,
                  self.lineNumber, self.nSamples, self.functionName,
                  self.nCalls)


class MonitoringDataFactory(factory.Factory):

    class Meta:
        model = MonitoringDataGenerator

    commitHash = "d0eb7082f4dd5dfce4c543e21299fb2e5774f70b"
    id = "30d376d2-fc7e-10d5-d51fe33373fd"
    publicIP = "187.2.167.60"
    timestamp = int(1531490785464)
    application = "nugvjtNBxHbjBnqbcFZvjn"
    macAddressHash = "d1dd34825af8599b78bd5f4a1d7d186e"
    lineNumber = int(836)
    nSamples = int(5745)
    functionName = "root"
    nCalls = 0


class ConfigGenerator(object):
    def __init__(self, brokers, prof_topic,
                 event_topic, log_topic, user_metrics_topic):
        self.brokers = brokers
        self.prof_topic = prof_topic
        self.event_topic = event_topic
        self.log_topic = log_topic
        self.user_metrics_topic = user_metrics_topic

    def __str__(self):
        return '{"brokers": ["%s"], "prof_topic": "%s", "event_topic": ' \
               '"%s", "log_topic": "%s", "user_metrics_topic": "%s"}' \
                % (self.brokers, self.prof_topic, self.event_topic,
                   self.log_topic, self.user_metrics_topic)


class ConfigFactory(factory.Factory):

    class Meta:
        model = ConfigGenerator

    brokers = "brokers-staging.feeds.auklet.io:9093"
    prof_topic = "profiler"
    event_topic = "events"
    log_topic = "logs"
    user_metrics_topic = "user_metrics"


class StackTraceGenerator(object):
    def __init__(self, functionName, lineNumber, nCalls, nSamples):
        self.functionName = functionName
        self.lineNumber = lineNumber
        self.nCalls = nCalls
        self.nSamples = nSamples

    def __str__(self):
        return '''{'callees': [],\n 'filePath': None,\n ''' \
               ''''functionName': '%s',\n 'lineNumber': %d,\n ''' \
               ''''nCalls': %d,\n 'nSamples': %d}''' \
               % (self.functionName, self.lineNumber,
                  self.nCalls, self.nSamples)


class StackTraceFactory(factory.Factory):

    class Meta:
        model = StackTraceGenerator

    functionName = "root"
    lineNumber = 1
    nCalls = 1
    nSamples = 1

class SingleNestedStackGenerator(object):
    def __init__(self, callees_functionName, callees_lineNumber,
                 callees_nCalls, callees_nSamples, functionName,
                 lineNumber, nCalls, nSamples):
        self.callees_functionName = callees_functionName
        self.callees_lineNumber = callees_lineNumber
        self.callees_nCalls = callees_nCalls
        self.callees_nSamples = callees_nSamples
        self.functionName = functionName
        self.lineNumber = lineNumber
        self.nCalls = nCalls
        self.nSamples = nSamples

    def __str__(self):
        return '''{'callees': [{'callees': [],\n''' \
               '''              'filePath': None,\n''' \
               '''              'functionName': '%s',\n''' \
               '''              'lineNumber': %d,\n''' \
               '''              'nCalls': %d,\n''' \
               '''              'nSamples': %d}],\n 'filePath': None,\n''' \
               ''' 'functionName': '%s',\n 'lineNumber': %d,\n''' \
               ''' 'nCalls': %d,\n 'nSamples': %d}''' \
               % (self.callees_functionName, self.callees_lineNumber,
                  self.callees_nCalls, self.callees_nSamples,
                  self.functionName, self.lineNumber, self.nCalls,
                  self.nSamples)


class SingleNestedStackTraceFactory(factory.Factory):

    class Meta:
        model = SingleNestedStackGenerator

    callees_functionName = ""
    callees_lineNumber = 0
    callees_nCalls = 1
    callees_nSamples = 1

    functionName = "root"
    lineNumber = 1
    nCalls = 1
    nSamples = 1
