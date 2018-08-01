import os
import sys
import ast
import json
import msgpack
import zipfile
import unittest
import paho.mqtt.client as mqtt

from mock import patch
from kafka.errors import KafkaError
from tests import data_factory

from auklet.base import Client
from auklet.utils import *
from auklet.broker import Profiler, KafkaClient, MQTTClient


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

    def build_test_load_kafka_conf(self, file):
        with patch(file) as _file:
            _file.side_effect = OSError
            self.assertFalse(self.profiler._load_conf())

    def test_load_kafka_conf(self):
        filename = self.client.com_config_filename
        with open(filename, "w") as config:
            config.write(json.dumps(self.config))
        self.assertTrue(self.profiler._load_conf())
        open(filename, "w").close()

        if sys.version_info < (3,):
            self.build_test_load_kafka_conf("__builtin__.open")
        else:
            self.build_test_load_kafka_conf("builtins.open")

    def test_get_certs(self):
        self.assertFalse(self.profiler._get_certs())

        class urlopen:
            def __init__(self, *args, **kwargs):
                pass

            def read(self):
                with open("key.pem.zip", "rb") as file:
                    return file.read()

        if sys.version_info < (3,):
            patcher = patch('auklet.base.Request')
            patcher.return_value = "http://api-staging.auklet.io"
            with patch('auklet.base.urlopen') as _urlopen:
                _urlopen.side_effect = urlopen
                with patch('io.BytesIO') as _bytesio:
                    _bytesio.return_value = "key.pem.zip"
                    os.system("touch key.pem")
                    with zipfile.ZipFile("key.pem.zip", "w") as zip:
                        zip.write("key.pem")
                        if sys.version_info < (3,):
                            self.assertFalse(self.profiler._get_certs())
                        else:
                            self.assertTrue(self.profiler._get_certs())
        else:
            with patch('auklet.base.Request') as _request:
                _request.return_value = "http://api-staging.auklet.io"
                with patch('auklet.base.urlopen') as _urlopen:
                    _urlopen.side_effect = urlopen
                    self.assertFalse(self.profiler._get_certs())
        recreate_files()

    def test_read_from_conf(self):
        self.assertIsNone(self.profiler._read_from_conf(self.data))

    def test_create_producer(self):
        self.assertIsNone(self.profiler.create_producer())

    def test_produce(self):
        self.assertIsNone(self.profiler.produce(self.data))


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
            return True

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

    def test_read_from_conf(self):
        self.broker._read_from_conf({"brokers": [],
                                     "prof_topic": "",
                                     "event_topic": "",
                                     "log_topic": ""})
        self.assertIsNotNone(self.broker.brokers)
        self.assertIsNotNone(self.broker.producer_types)

    def test_write_conf(self):
        filename = self.broker.com_config_filename
        self.broker._write_conf(info=self.config)
        self.assertGreater(os.path.getsize(filename), 0)
        open(filename, "w").close()


    def test_get_certs(self):
        with patch('auklet.utils.build_url') as mock_zip_file:
            with patch('zipfile.ZipFile') as mock_url:
                mock_url.file_list.return_value = ""
                mock_zip_file.return_value = "http://api-staging.auklet.io"
                self.assertTrue(self.broker._get_certs())

    def test_write_to_local(self):
        open(self.client.offline_filename, "w").close()
        if sys.version_info < (3,):
            self.broker._write_to_local(data=self.data, data_type="event")
        else:
            self.broker._write_to_local(
                data=msgpack.packb(self.data), data_type="")
        self.assertGreater(os.path.getsize(self.client.offline_filename), 0)
        clear_file(self.client.offline_filename)

        os.system("rm -R .auklet")
        self.assertFalse(self.broker._write_to_local(self.data, data_type=""))
        os.system("mkdir .auklet")
        os.system("touch %s" % self.client.offline_filename)
        recreate_files()

    def test_produce_from_local(self):
        open(self.client.offline_filename, "w").close()

        def _produce(self, data, data_type):
            global test_produced_data  # used to tell data was produced
            test_produced_data = data

        with patch('auklet.broker.KafkaClient._produce', new=_produce):
            with open(self.client.offline_filename, "w") as offline:
                offline.write("event::")
                if sys.version_info < (3,):
                    offline.write(str(self.data))
                else:
                    offline.write(str(msgpack.packb(self.data)))
                offline.write("\n")
            self.broker._produce_from_local()
        self.assertIsNotNone(test_produced_data)  # global used here

        os.system("rm -R .auklet")
        self.assertFalse(self.broker._produce_from_local())
        os.system("mkdir .auklet")
        recreate_files()

    def test_kafka_error_callback(self):
        self.broker._error_callback(msg="", error="", data_type="")
        self.assertGreater(os.path.getsize(self.client.offline_filename), 0)
        clear_file(self.client.offline_filename)

    def test__produce(self):
        pass
        # class KafkaProducer:
        #     def __init__(self, **configs):
        #         pass
        #
        #     def send(self, data_type, value, key):
        #         print(value)
        #         global test__produce_value
        #         test__produce_value = value
        #
        # with patch('kafka.KafkaProducer') as _KafkaProducer:
        #     with patch('auklet.broker.KafkaClient.create_producer') as _create_producer:
        #         _KafkaProducer.side_effect = KafkaProducer
        #         _create_producer.return_value = True
        #         self.broker.create_producer()
        #         self.broker._produce(self.data)

    def _produce(self, data, data_type="monitoring"):
        global test_produce_data  # used to tell data was produced
        test_produce_data = data

    def check_data_limit(self, data, data_current, offline=False):
        if not error or offline:  # global used here
            return True
        else:
            raise KafkaError

    def write_to_local(self, data, data_type):
        global write_to_local_data
        write_to_local_data = data

    def test_produce(self):
        global error  # used to tell which test case is being tested
        error = False

        with patch('auklet.broker.KafkaClient._produce', new=self._produce):
            self.broker.producer = True
            with patch('auklet.base.Client.check_data_limit',
                       new=self.check_data_limit):
                with open(self.client.offline_filename, "w") as offline:
                    offline.write("event::")
                    if sys.version_info < (3,):
                        offline.write(str(self.data))
                    else:
                        offline.write(str(msgpack.packb(self.data)))
                    offline.write("\n")
                    self.broker.produce(self.data)
                self.assertNotEqual(
                    str(test_produce_data), None)  # global used here
                error = True
                self.broker.produce(self.data)
                self.assertGreater(
                    os.path.getsize(self.client.offline_filename), 0)
            with patch('auklet.base.Client.check_data_limit') \
                    as self._check_data_limit:
                with patch('auklet.broker.KafkaClient._write_to_local',
                           new=self.write_to_local):
                    self._check_data_limit.return_value = False
                    self.broker.produce(self.data)
                    self.assertIsNotNone(write_to_local_data)


class TestMQTTBroker(unittest.TestCase):
    # print("During the running of these tests, there will be TypeError"
    #       "exceptions.  That is expected.  It is unable to connect.")
    data = ast.literal_eval(str(data_factory.MonitoringDataFactory()))
    config = ast.literal_eval(str(data_factory.ConfigFactory()))

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

    class Mock_Client:
        def __init__(self):
            pass

        def tls_set(self, ca_certs):
            pass

        def tls_set_context(self, ctx):
            pass

        def connect_async(self, broker, port):
            pass

        def loop_start(self):
            global create_producer_pass
            create_producer_pass = True

    def test_create_producer(self):
        global create_producer_pass
        create_producer_pass = False

        self.patcher2.stop()

        with patch('auklet.broker.MQTTClient._get_certs') as get_certs:
            with patch('paho.mqtt.client.Client') as _Client:
                _Client.side_effect = self.Mock_Client
                get_certs.return_value = True
                os.system("touch .auklet/ck_ca.pem")
                self.broker.create_producer()
                self.assertTrue(create_producer_pass)
        self.patcher2.start()

    def test_produce(self):
        self.assertIsNone(self.broker.produce(str(self.data)))
        self.assertRaises(TypeError, lambda: self.broker.produce(self.data))


if __name__ == '__main__':
    unittest.main()