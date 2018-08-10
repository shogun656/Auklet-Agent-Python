import os
import sys
import ast
import json
import unittest

from mock import patch
from tests import data_factory

from auklet.monitoring.processing import Client
from auklet.broker import Profiler, MQTTClient


def recreate_files():
    os.system("touch .auklet/version")
    os.system("touch .auklet/communication")
    os.system("touch .auklet/usage")
    os.system("touch .auklet/limits")


class TestProfiler(unittest.TestCase):
    data = ast.literal_eval(str(data_factory.MonitoringDataFactory()))
    config = ast.literal_eval(str(data_factory.ConfigFactory()))

    def setUp(self):
        self.client = Client(
            apikey="", app_id="", base_url="https://api-staging.auklet.io/")

        Profiler.__abstractmethods__ = frozenset()
        self.profiler = Profiler(self.client)

    def test_write_conf(self):
        self.profiler._write_conf(self.config)
        self.assertGreater(os.path.getsize(self.client.com_config_filename), 0)
        open(self.client.com_config_filename, "w").close()

    def test_load_conf(self):
        filename = self.client.com_config_filename
        with open(filename, "w") as config:
            config.write(json.dumps(self.config))
        self.assertTrue(self.profiler._load_conf())
        open(filename, "w").close()

        if sys.version_info < (3,):
            self.build_test_load_conf("__builtin__.open")
        else:
            self.build_test_load_conf("builtins.open")

        self.assertFalse(self.profiler._load_conf())

    def test_get_certs(self):
        class urlopen:
            @staticmethod
            def read():
                with open("key.pem.zip", "rb") as file:
                    return file.read()

        self.assertFalse(self.profiler._get_certs())
        with patch('auklet.broker.urlopen') as _urlopen:
            _urlopen.return_value = urlopen
            self.assertTrue(self.profiler._get_certs())

    def test_read_from_conf(self):
        self.assertIsNone(self.profiler._read_from_conf(self.data))

    def test_create_producer(self):
        self.assertIsNone(self.profiler.create_producer())

    def test_produce(self):
        self.assertIsNone(self.profiler.produce(self.data))

    def build_test_load_conf(self, file):
        with patch(file) as _file:
            _file.side_effect = OSError
            self.assertFalse(self.profiler._load_conf())


class TestMQTTBroker(unittest.TestCase):
    data = ast.literal_eval(str(data_factory.MonitoringDataFactory()))
    config = ast.literal_eval(str(data_factory.ConfigFactory()))

    def setUp(self):
        self.client = Client(
            apikey="", app_id="", base_url="https://api-staging.auklet.io/")
        self.broker = MQTTClient(self.client)

    def test_read_from_conf(self):
        self.broker._read_from_conf({"brokers": [],
                                     "port": "",
                                     "prof_topic": "",
                                     "event_topic": "",
                                     "log_topic": ""})
        self.assertIsNotNone(self.broker.brokers)
        self.assertIsNotNone(self.broker.port)
        self.assertIsNotNone(self.broker.producer_types)

    def test_on_disconnect(self):
        def debug(msg):
            global debug_msg
            debug_msg = msg

        with patch('logging.debug') as _debug:
            _debug.side_effect = debug
            self.broker.on_disconnect("", 1)
            self.assertIsNotNone(debug_msg)

    def test_create_producer(self):
        global create_producer_pass
        create_producer_pass = False

        with patch('auklet.broker.MQTTClient._get_certs') as get_certs:
            with patch('paho.mqtt.client.Client') as _Client:
                _Client.side_effect = self.MockClient
                get_certs.return_value = True
                os.system("touch .auklet/ck_ca.pem")
                self.broker.create_producer()
                self.assertTrue(create_producer_pass)

    def test_produce(self):
        with patch('paho.mqtt.client.Client.publish') as _publish:
            with patch('auklet.broker.Profiler._get_certs') as get_certs:
                get_certs.return_value = True
                _publish.side_effect = self.publish
                self.broker.create_producer()
                self.broker.produce(str(self.data))
                self.assertIsNotNone(test_produce_payload)

    class MockClient:
        def __init__(self):
            pass

        def tls_set(self, ca_certs):
            pass

        def tls_set_context(self):
            pass

        def connect_async(self, broker, port):
            pass

        def enable_logger(self):
            pass

        def loop_start(self):
            global create_producer_pass
            create_producer_pass = True

    @staticmethod
    def publish(data_type, payload):
        global test_produce_payload
        test_produce_payload = payload


if __name__ == '__main__':
    unittest.main()
