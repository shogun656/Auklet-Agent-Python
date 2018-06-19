from __future__ import absolute_import, unicode_literals

import abc

import io
import ssl
import json
import zipfile
from kafka import KafkaProducer
from kafka.errors import KafkaError
from auklet import utils
from auklet.utils import b, u

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError, URLError

__all__ = ["Profiler", "KafkaClient", "MQTTClient"]

# compatible with Python 2 *and* 3
# https://stackoverflow.com/questions/35673474/using-abc-abcmeta-in-a-way-it-is-compatible-both-with-python-2-7-and-python-3-5
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class Profiler(ABC):
    producer = None
    brokers = None
    com_config_filename = ".auklet/communication"

    def __init__(self):
        self._load_conf()
        self.create_producer()

    def _get_brokers(self):
        res = utils.open_auklet_url(
            self._build_url("private/devices/config/"))
        if res is None:
            return self._load_conf()
        info = json.loads(u(res.read()))
        self._write_conf(info)
        self._read_from_conf(info)

    def _write_conf(self, info):
        with open(self.com_config_filename, "w") as conf:
            conf.write(json.dumps(info))

    def _load_conf(self):
        try:
            with open(self.com_config_filename, "r") as conf:
                json_data = conf.read()
                if json_data:
                    data = json.loads(json_data)
                    self._read_from_conf(data)
                    return True
                else:
                    return False
        except OSError:
            return False

    def _get_certs(self):
        url = Request(self._build_url("private/devices/certificates/"),
                      headers={"Authorization": "JWT %s" % self.apikey})
        try:
            try:
                res = urlopen(url)
            except HTTPError as e:
                # Allow for accessing redirect w/o including the
                # Authorization token.
                res = urlopen(e.geturl())
        except URLError:
            return False
        mlz = zipfile.ZipFile(io.BytesIO(res.read()))
        for temp_file in mlz.filelist:
            filename = ".auklet/%s.pem" % temp_file.filename
            self._create_file(filename)
            f = open(filename, "wb")
            f.write(mlz.open(temp_file.filename).read())
        return True

    @abc.abstractmethod
    def _read_from_conf(self, data):
        pass

    @abc.abstractmethod
    def create_producer(self):
        pass

    @abc.abstractmethod
    def produce(self, data, data_type="monitoring"):
        pass


class KafkaClient(Profiler):
    def __init__(self):
        super(KafkaClient, self).__init__()

    def _read_from_conf(self, data):
        self.brokers = data['brokers']
        self.producer_types = {
            "monitoring": data['prof_topic'],
            "event": data['event_topic'],
            "log": data['log_topic']
        }

    def _kafka_error_callback(self, error, msg):
        self._write_to_local(msg)

    def create_producer(self):
        if self._get_certs():
            try:
                ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ctx.options &= ~ssl.OP_NO_SSLv3
                self.producer = KafkaProducer(**{
                    "bootstrap_servers": self.brokers,
                    "ssl_cafile": ".auklet/ck_ca.pem",
                    "security_protocol": "SSL",
                    "ssl_check_hostname": False,
                    "value_serializer": lambda m: b(json.dumps(m)),
                    "ssl_context": ctx
                })
            except (KafkaError, Exception):
                # TODO log off to kafka if kafka fails to connect
                pass

    def produce(self, data, data_type="monitoring"):
        self.producer.send(self.producer_types[data_type],
                           value=data) \
            .add_errback(self._kafka_error_callback, msg=data)


class MQTTClient(Profiler):
    def __init__(self):
        super(MQTTClient, self).__init__()

    def _read_from_conf(self, data):
        self.brokers = data['brokers']
        self.producer_types = {
            "monitoring": data['prof_topic'],
            "event": data['event_topic'],
            "log": data['log_topic']
        }

    def _kafka_error_callback(self, error, msg):
        self._write_to_local(msg)

    def create_producer(self):
        if self._get_certs():
            try:
                ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ctx.options &= ~ssl.OP_NO_SSLv3
                self.producer = KafkaProducer(**{
                    "bootstrap_servers": self.brokers,
                    "ssl_cafile": ".auklet/ck_ca.pem",
                    "security_protocol": "SSL",
                    "ssl_check_hostname": False,
                    "value_serializer": lambda m: b(json.dumps(m)),
                    "ssl_context": ctx
                })
            except (KafkaError, Exception):
                # TODO log off to kafka if kafka fails to connect
                pass

    def produce(self, data, data_type="monitoring"):
        self.producer.send(self.producer_types[data_type],
                           value=data) \
            .add_errback(self._kafka_error_callback, msg=data)
