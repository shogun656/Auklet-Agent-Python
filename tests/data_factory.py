import factory


class MonitoringDataGenerator(object):
    def __init__(self, commitHash, id, publicIP, timestamp, application,
                 macAddressHash, lineNumber, nSamples, functionName):
        self.commitHash = commitHash
        self.id = id
        self.publicIP = publicIP
        self.timestamp = timestamp
        self.application = application
        self.macAddressHash = macAddressHash

        self.lineNumber = lineNumber
        self.nSamples = nSamples
        self.functionName = functionName

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
               '"functionName": "%s"' \
               '}]}' \
               % (self.commitHash, self.id, self.publicIP,
                  self.timestamp, self.application, self.macAddressHash,
                  self.lineNumber, self.nSamples, self.functionName)


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
    def __init__(self, functionName, lineNumber, nSamples):
        self.functionName = functionName
        self.lineNumber = lineNumber
        self.nSamples = nSamples

    def __str__(self):
        return '''{'callees': [],\n 'filePath': None,\n ''' \
               ''''functionName': '%s',\n 'lineNumber': %d,\n ''' \
               ''''nSamples': %d}''' \
               % (self.functionName, self.lineNumber, self.nSamples)


class StackTraceFactory(factory.Factory):

    class Meta:
        model = StackTraceGenerator

    functionName = "root"
    lineNumber = 1
    nSamples = 1

class SingleNestedStackGenerator(object):
    def __init__(self, callees_functionName, callees_lineNumber,
                 callees_nSamples, functionName,
                 lineNumber, nSamples):
        self.callees_functionName = callees_functionName
        self.callees_lineNumber = callees_lineNumber
        self.callees_nSamples = callees_nSamples
        self.functionName = functionName
        self.lineNumber = lineNumber
        self.nSamples = nSamples

    def __str__(self):
        return '''{'callees': [{'callees': [],''' \
               '''              'filePath': None,''' \
               '''              'functionName': '%s',''' \
               '''              'lineNumber': %d,''' \
               '''              'nSamples': %d}],''' \
               '''              'filePath': None,''' \
               ''' 'functionName': '%s', 'lineNumber': %d,''' \
               ''' 'nSamples': %d}''' \
               % (self.callees_functionName, self.callees_lineNumber,
                  self.callees_nSamples, self.functionName,
                  self.lineNumber, self.nSamples)


class SingleNestedStackTraceFactory(factory.Factory):

    class Meta:
        model = SingleNestedStackGenerator

    callees_functionName = ""
    callees_lineNumber = 0
    callees_nSamples = 1

    functionName = "root"
    lineNumber = 1
    nSamples = 1
