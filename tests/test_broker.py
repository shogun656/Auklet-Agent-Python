import os
import ast
import json
import msgpack
import unittest
import paho.mqtt.client as mqtt

from mock import patch
from kafka.errors import KafkaError
from tests import data_factory

from auklet.base import Client
from auklet.utils import *
from auklet.broker import KafkaClient, MQTTClient


class TestKafkaBroker(unittest.TestCase):
    data = ast.literal_eval(str(data_factory.MonitoringDataFactory()))
    config = ast.literal_eval(str(data_factory.ConfigFactory()))

    def setUp(self):
        def _load_conf(self):
            self.brokers = ["api-staging.auklet.io:9093"]
            self.producer_types = {
                "monitoring": "profiling",
                "event": "events",
                "log": "logging"
            }

        def _get_certs(self):
            return True
        self.patcher = patch(
            'auklet.broker.KafkaClient._load_conf', new=_load_conf)
        self.patcher2 = patch(
            'auklet.broker.KafkaClient._get_certs', new=_get_certs)
        self.patcher.start()
        self.patcher2.start()
        self.client = Client(
            apikey="", app_id="", base_url="https://api-staging.auklet.io/")
        self.broker = KafkaClient(self.client)

    def tearDown(self):
        self.patcher.stop()
        self.patcher2.stop()

    def test_get_brokers(self):
        pass

    def test_write_kafka_conf(self):
        filename = self.client.com_config_filename
        self.broker._write_conf(info=self.config)
        self.assertGreater(os.path.getsize(filename), 0)
        open(filename, "w").close()

    def test_load_conf(self):
        self.patcher.stop()
        filename = self.client.com_config_filename
        with open(filename, "w") as config:
            config.write(json.dumps(self.config))
        self.assertTrue(self.broker._load_conf())
        open(filename, "w").close()
        self.patcher.start()

    def test_get_certs(self):
        with patch('auklet.utils.build_url') as mock_zip_file:
            with patch('zipfile.ZipFile') as mock_url:
                mock_url.file_list.return_value = ""
                mock_zip_file.return_value = "http://api-staging.auklet.io"
                self.assertTrue(self.broker._get_certs())

    def test_write_to_local(self):
        self.broker._write_to_local(data=self.data, data_type="")
        self.assertGreater(os.path.getsize(self.client.offline_filename), 0)
        clear_file(self.client.offline_filename)

        os.system("rm -R .auklet")
        self.assertFalse(
            self.broker._write_to_local(data=self.data, data_type=""))
        os.system("mkdir .auklet")
        os.system("touch %s" % self.client.offline_filename)
        os.system("touch .auklet/version")

    def test_produce_from_local(self):
        def _produce(self, data, data_type):
            global test_produced_data  # used to tell data was produced
            test_produced_data = data

        with patch('auklet.broker.KafkaClient._produce', new=_produce):
            with open(self.client.offline_filename, "a") as offline:
                offline.write("event:")
                offline.write(str(msgpack.packb({"stackTrace": "data"})))
                offline.write("\n")
            self.broker._produce_from_local()
        self.assertIsNotNone(test_produced_data)  # global used here

        os.system("rm -R .auklet")
        self.assertFalse(self.broker._produce_from_local())
        os.system("mkdir .auklet")
        os.system("touch %s" % self.client.offline_filename)
        os.system("touch .auklet/version")

    def test_kafka_error_callback(self):
        self.broker._error_callback(msg="", error="", data_type="")
        self.assertGreater(os.path.getsize(self.client.offline_filename), 0)
        clear_file(self.client.offline_filename)

    def test__produce(self):
        pass

    def test_produce(self):
        global error  # used to tell which test case is being tested
        error = False

        def _produce(self, data, data_type="monitoring"):
            global test_produce_data  # used to tell data was produced
            test_produce_data = data

        def check_data_limit(self, data, data_current, offline=False):
            if not error or offline:  # global used here
                return True
            else:
                raise KafkaError

        with patch('auklet.broker.KafkaClient._produce', new=_produce):
            with patch('auklet.base.Client.check_data_limit',
                       new=check_data_limit):
                self.broker.producer = True
                with open(self.client.offline_filename, "w") as offline:
                    offline.write("event:")
                    offline.write(str(msgpack.packb(self.data)))
                    offline.write("\n")
                self.broker.produce(self.data)
                self.assertNotEqual(
                    str(test_produce_data), None)  # global used here
                error = True
                self.broker.produce(self.data)
                self.assertGreater(
                    os.path.getsize(self.client.offline_filename), 0)


class TestMQTTBroker(unittest.TestCase):
    data = ast.literal_eval(str(data_factory.MonitoringDataFactory()))

    def setUp(self):
        def _load_conf(self):
            self.brokers = ["mqtt"]
            self.port = 1883
            self.producer_types = {
                "monitoring": "python/agent/profiling",
                "event": "python/agent/events",
                "log": "python/agent/logging"
            }

        def create_producer(self):
            # Make non SSL producer for testing
            self.producer = mqtt.Client()
            self.producer.on_disconnect = self.on_disconnect
            self.producer.connect_async(self.brokers, self.port)
            self.producer.loop_start()
        self.patcher = patch(
            'auklet.broker.MQTTClient._load_conf', new=_load_conf)
        self.patcher2 = patch(
            'auklet.broker.MQTTClient.create_producer', new=create_producer)
        self.patcher.start()
        self.patcher2.start()
        self.client = Client(
            apikey="", app_id="", base_url="https://api-staging.auklet.io/")
        self.broker = MQTTClient(self.client)

    def tearDown(self):
        self.patcher.stop()
        self.patcher2.stop()

    def test_produce(self):
        def produce(self, data, data_type="monitoring"):
            global test_produce_data  # used to tell data was produced
            test_produce_data = data

        with patch('auklet.broker.MQTTClient._produce', new=produce):
            self.broker.produce(self.data)
            self.assertNotEqual(
                str(test_produce_data), None)  # global used here


if __name__ == '__main__':
    unittest.main()
