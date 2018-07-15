import os
import unittest
from mock import patch, Mock
from datetime import datetime
import json

from urllib.error import HTTPError

from tests import data_factory

from kafka.errors import KafkaError
from ipify.exceptions import IpifyException

from auklet.base import *
from auklet.stats import MonitoringTree
from auklet.errors import AukletConfigurationError


class TestClient(unittest.TestCase):
    data = str(data_factory.MonitoringDataFactory())
    def setUp(self):
        def _get_kafka_brokers(self):
            self.brokers = ["api-staging.auklet.io:9093"]
            self.producer_types = {
                "monitoring": "profiling",
                "event": "events",
                "log": "logging"
            }
        self.patcher = patch(
            'auklet.base.Client._get_kafka_brokers', new=_get_kafka_brokers)
        self.patcher.start()
        self.client = Client(
            apikey="", app_id="", base_url="https://api-staging.auklet.io/")
        self.monitoring_tree = MonitoringTree()

    def tearDown(self):
        self.patcher.stop()

    def test___init__(self):
        def _get_kafka_certs(self):
            return True

        class KafkaProducer(object):
            global test__init__producer
            test__init__producer = True

        with patch('auklet.base.Client._get_kafka_certs',
                   new=_get_kafka_certs):
            with patch('kafka.KafkaProducer', new=KafkaProducer):
                self.client.__init__()
                self.assertTrue(test__init__producer)

    def test_create_file(self):
        files = ['.auklet/local.txt', '.auklet/limits',
                 '.auklet/usage', '.auklet/communication']
        for f in files:
            file = False
            if os.path.isfile(f):
                file = True
            self.assertTrue(file)

    def test_build_url(self):
        extension = str("private/devices/config/")
        self.assertEqual(
            self.client._build_url(extension),
            self.client.base_url + extension)

    def test_open_auklet_url(self):
        url = self.client.base_url + "private/devices/config/"
        self.assertRaises(
            AukletConfigurationError,
            lambda: self.client._open_auklet_url(url))
        url = "http://google.com/"
        self.assertNotEqual(self.client._open_auklet_url(url), None)

    def test_get_config(self):
        pass

    def test_get_kafka_brokers(self):
        pass

    def test_write_kafka_conf(self):
        filename = self.client.com_config_filename
        self.client._write_kafka_conf(info=str(data_factory.ConfigFactory()))
        self.assertGreater(os.path.getsize(filename), 0)
        open(filename, "w").close()

    def test_load_kafka_conf(self):
        filename = self.client.com_config_filename
        with open(filename, "w") as my_file:
            my_file.write(str(data_factory.ConfigFactory()))
        self.assertTrue(self.client._load_kafka_conf())
        open(filename, "w").close()

    def test_load_limits(self):
        loaded = True
        if self.client._load_limits():
            loaded = False
        self.assertTrue(loaded)

    def test_get_kafka_certs(self):
        with patch('auklet.base.Client._build_url') as mock_zip_file:
            with patch('zipfile.ZipFile') as mock_url:
                mock_url.file_list.return_value = ""
                mock_zip_file.return_value = "http://api-staging.auklet.io"
                self.assertTrue(self.client._get_kafka_certs())

    def test_write_to_local(self):
        self.client._write_to_local(self.data)
        self.assertGreater(os.path.getsize(self.client.offline_filename), 0)
        self.client._clear_file(self.client.offline_filename)

        os.system("rm -R .auklet")
        self.assertFalse(self.client._write_to_local(self.data))
        os.system("mkdir .auklet")
        os.system("touch %s" % self.client.offline_filename)
        os.system("touch .auklet/version")

    def test_clear_file(self):
        file_name = "unit_test_temp"
        with open(file_name, "w") as unit_test_temp_file:
            unit_test_temp_file.write("data")
        self.client._clear_file(file_name)
        self.assertEqual(os.path.getsize(file_name), 0)
        os.remove(file_name)

    def test_produce_from_local(self):
        def _produce(self, data, data_type):
            global test_produced_data
            test_produced_data = data
        with patch('auklet.base.Client._produce', new=_produce):
            with open(self.client.offline_filename, 'w') as offline:
                offline.write(json.dumps({'stackTrace': 'data'}))
            self.client._produce_from_local()
        self.assertEqual(test_produced_data, {'stackTrace': 'data'})

        os.system("rm -R .auklet")
        self.assertFalse(self.client._produce_from_local())
        os.system("mkdir .auklet")
        os.system("touch %s" % self.client.offline_filename)
        os.system("touch .auklet/version")

    def test_build_usage_json(self):
        data = self.client._build_usage_json()
        for value in data.values():
            self.assertNotEqual(value, None)

    def test_update_usage_file(self):
        os.system("rm -R .auklet")
        self.assertFalse(self.client._update_usage_file())
        os.system("mkdir .auklet")
        os.system("touch %s" % self.client.offline_filename)
        os.system("touch .auklet/version")

    def test_check_data_limit(self):
        self.client.offline_limit = None
        self.assertTrue(
            self.client._check_data_limit(
                data=self.data, current_use=0, offline=True))

        self.client.data_limit = None
        self.assertTrue(
            self.client._check_data_limit(data=self.data, current_use=0))

        self.client.offline_limit = self.client.data_limit = 1
        self.assertFalse(
            self.client._check_data_limit(data=self.data, current_use=0))

        self.client.data_limit = 1000
        self.client._check_data_limit(
            data=self.data, current_use=0, offline=True)
        self.assertNotEqual(self.client.offline_current, 0)

        self.client._check_data_limit(
            data=self.data, current_use=0)
        self.assertNotEqual(self.client.data_current, 0)

        self.assertTrue(
            self.client._check_data_limit(data=self.data, current_use=0))

    def test_kafka_error_callback(self):
        self.client._kafka_error_callback(msg="", error="")
        self.assertGreater(os.path.getsize(self.client.offline_filename), 0)
        self.client._clear_file(self.client.offline_filename)

    def test_update_network_metrics(self):
        self.client.update_network_metrics(1000)
        self.assertNotEqual(self.client.system_metrics, None)
        self.client.system_metrics = None

    def test_check_date(self):
        self.client.data_day = datetime.today().day
        self.client.data_current = 1000
        self.client.reset_data = True
        self.client.check_date()
        self.assertEqual(self.client.data_current, 0)
        self.assertEqual(self.client.reset_data, False)

    def test_update_limits(self):
        none = True
        cellular_data_limit = None
        storage_limit = None
        cell_plan_date = 1

        def _get_config(self):
            if none:
                return None
            else:
                return {"storage":
                        {"storage_limit": storage_limit},
                        "emission_period": 60,
                        "features":
                        {"performance_metrics": True,
                         "user_metrics": False},
                        "data":
                        {"cellular_data_limit": cellular_data_limit,
                         "normalized_cell_plan_date": cell_plan_date}}

        with patch('auklet.base.Client._get_config', new=_get_config):
            self.assertEqual(self.client.update_limits(), 60)
            none = False

            cellular_data_limit = 1000
            self.client.update_limits()
            self.assertEqual(self.client.data_limit, 1000000000.0)
            cellular_data_limit = None

            storage_limit = 1000
            self.client.update_limits()
            self.assertEqual(self.client.offline_limit, 1000000000.0)
            storage_limit = None

            cell_plan_date = 10
            self.client.update_limits()
            self.assertEqual(self.client.data_day, 10)
            cell_plan_date = 1

            self.assertEqual(self.client.update_limits(), 60000)

    def test_build_event_data(self):
        def get_mock_event(exc_type=None, tb=None, tree=None, abs_path=None):
            return {"stackTrace":
                    [{"functionName": "",
                        "filePath": "",
                        "lineNumber": 0,
                        "locals":
                        {"key": "value"}}]}

        with patch('auklet.base.Event', new=get_mock_event):
            self.assertNotEqual(
                self.client.build_event_data(
                    type=None, traceback="", tree=""), None)

    def test_build_log_data(self):
        self.assertNotEqual(
            self.client.build_log_data(
                msg='msg', data_type='data_type', level='level'), None)

    def test__produce(self):
        pass

    def test_produce(self):
        global error
        error = False

        def _produce(self, data, data_type="monitoring"):
            global test_produce_data
            test_produce_data = str(data).replace("'", '"')

        def _check_data_limit(self, data, data_current, offline=False):
            if not error or offline:
                return True
            else:
                raise KafkaError

        with patch('auklet.base.Client._produce', new=_produce):
            with patch('auklet.base.Client._check_data_limit',
                       new=_check_data_limit):
                self.client.producer = True

                with open(self.client.offline_filename, 'w') as offline:
                    offline.write(self.data)
                self.client.produce(self.data)
                self.assertEqual(test_produce_data, self.data)

                error = True
                self.client.produce(self.data)
                self.assertGreater(os.path.getsize(self.client.offline_filename), 0)

class TestRunnable(unittest.TestCase):
    def setUp(self):
        self.runnable = Runnable()

    def test_is_running(self):
        self.assertFalse(self.runnable.is_running())
        self.runnable._running = True
        self.assertTrue(self.runnable.is_running())
        self.runnable._running = None

    def test_start(self):
        self.runnable._running = True
        self.assertRaises(RuntimeError, lambda: self.runnable.start())
        self.runnable._running = None

        def next(self):
            raise StopIteration

        with patch('auklet.base.next', new=next):
            self.assertRaises(Exception, lambda: self.runnable.start())

        self.runnable._running = None

    def test_stop(self):
        self.runnable._running = None
        self.assertRaises(RuntimeError, lambda: self.runnable.stop())

        def next(self):
            raise StopIteration

        self.runnable._running = True
        with patch('auklet.base.next', new=next):
            self.runnable.stop()

    def test_run(self):
        self.assertTrue(self.run())

    def test___enter__(self):
        def start(self):
            global running
            running = True

        with patch('auklet.base.Runnable.start', new=start):
            self.runnable.__enter__()
            self.assertTrue(running)

    def test___exit__(self):
        pass


class Test(unittest.TestCase):
    def test_frame_stack(self):
        class FrameStack:
            f_back = None
        frame = FrameStack()
        self.assertNotEqual(frame_stack(frame), None)

    def test_get_mac(self):
        self.assertNotEqual(get_mac(), None)

    def test_get_commit_hash(self):
        with open(".auklet/version", "w") as my_file:
            my_file.write("commit_hash")
        self.assertNotEqual(get_commit_hash(), "")

        os.system("rm -R .auklet")
        self.assertEqual(get_commit_hash(), "")
        os.system("mkdir .auklet")
        os.system("touch .auklet/local.txt")
        os.system("touch .auklet/version")

    def test_get_abs_path(self):
        path = os.path.abspath(__file__)
        self.assertEqual(get_abs_path(path + "/.auklet"), path)

        with patch('os.path.abspath') as mock_abspath:
            mock_abspath.side_effect = IndexError
            self.assertEqual(get_abs_path(path), '')

    def test_get_device_ip(self):
        self.assertNotEqual(get_device_ip(), None)
        with patch('auklet.base.get_ip') as mock_error:
            mock_error.side_effect = IpifyException
            self.assertIsNone(get_device_ip())
            mock_error.side_effect = Exception
            self.assertIsNone(get_device_ip())

    def test_setup_thread_excepthook(self):
        pass


if __name__ == '__main__':
    unittest.main()
