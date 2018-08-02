import ast
import unittest
import paho.mqtt.client as mqtt

from mock import patch
from tests import data_factory

from auklet.monitoring.processing import Client
from auklet.broker import MQTTClient


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
            return True

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

        with patch('auklet.broker.MQTTClient.produce', new=produce):
            self.broker.produce(self.data)
            self.assertNotEqual(
                str(test_produce_data), None)  # global used here


if __name__ == '__main__':
    unittest.main()
