from __future__ import absolute_import

import abc
import ssl
import json
import logging
import paho.mqtt.client as mqtt

from auklet.utils import build_url, create_file, open_auklet_url, u

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError, URLError

__all__ = ["Profiler", "MQTTClient"]

# compatible with Python 2 *and* 3
# https://stackoverflow.com/questions/35673474/using-abc-abcmeta-in-a-way-it-is-compatible-both-with-python-2-7-and-python-3-5
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class Profiler(ABC):
    producer = None
    brokers = None
    client = None
    com_config_filename = ".auklet/communication"

    def __init__(self, client):
        self.client = client
        self._get_conf()
        self.create_producer()

    def _write_conf(self, info):
        with open(self.com_config_filename, "w") as conf:
            conf.write(json.dumps(info))

    def _get_conf(self):
        res = open_auklet_url(
            build_url(
                self.client.base_url, "private/devices/config/"
            ),
            self.client.apikey
        )
        loaded = json.loads(u(res.read()))
        self._write_conf(loaded)
        self._read_from_conf(loaded)

    def _get_certs(self):
        url = Request(
            build_url(self.client.base_url, "private/devices/certificates/"),
            headers={"Authorization": "JWT %s" % self.client.apikey})
        try:
            try:
                res = urlopen(url)
            except HTTPError as e:
                # Allow for accessing redirect w/o including the
                # Authorization token.
                res = urlopen(e.geturl())
        except URLError:
            return False
        filename = ".auklet/ca.pem"
        create_file(filename)
        f = open(filename, "wb")
        f.write(res.read())
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


class MQTTClient(Profiler):
    port = None

    def _read_from_conf(self, data):
        self.brokers = data['brokers']
        self.port = int(data['port'])
        self.producer_types = {
            "monitoring": "python/profiler/monitoring",
            "event": "python/events/event",
        }

    def on_disconnect(self, userdata, rc):
        if rc != 0:
            logging.debug("Unexpected disconnection from MQTT")

    def create_producer(self):
        if self._get_certs():
            self.producer = mqtt.Client()
            self.producer.enable_logger()
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(capath=".auklet/")
            context.options &= ~ssl.OP_NO_SSLv3
            self.producer.tls_set_context()

            self.producer.on_disconnect = self.on_disconnect
            self.producer.connect_async(self.brokers, self.port)
            self.producer.loop_start()

    def produce(self, data, data_type="monitoring"):
        self.producer.publish(self.producer_types[data_type], payload=data)
