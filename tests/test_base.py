import os
import unittest
from mock import patch

from tests import data_factory

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
        self.patcher = patch('auklet.base.Client._get_kafka_brokers', new=_get_kafka_brokers)
        self.patcher.start()
        self.client = Client(apikey="", app_id="", base_url="https://api-staging.auklet.io/")
        self.monitoring_tree = MonitoringTree()

    def tearDown(self):
        self.patcher.stop()

    def test_create_file(self):
        files = ['.auklet/local.txt', '.auklet/limits', '.auklet/usage', '.auklet/communication']
        for f in files:
            file = False
            if os.path.isfile(f):
                file = True
            self.assertTrue(file)

    def test_build_url(self):
        extension = str("private/devices/config/")
        self.assertEqual(self.client._build_url(extension), self.client.base_url + extension)

    def test_open_auklet_url(self):
        url = self.client.base_url + "private/devices/config/"
        self.assertRaises(AukletConfigurationError, lambda: self.client._open_auklet_url(url))
        url = "http://google.com/"
        self.assertNotEqual(self.client._open_auklet_url(url), None)

    @patch('auklet.base.Client._build_url')
    @patch('auklet.base.Client._get_config')
    def test_get_config(self, mock_conf, mock_url):
        _ = mock_conf
        mock_url.return_value = "http://api-staging.auklet.io"
        self.assertNotEqual(self.client._get_config(), None)

    def test_get_kafka_brokers(self):
        self.assertEqual(self.client._get_kafka_brokers(), None)

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

    @patch('auklet.base.Client._build_url')
    @patch('zipfile.ZipFile')
    def test_get_kafka_certs(self, mock_zip_file, mock_url):
        mock_zip_file.file_list.return_value = ""
        mock_url.return_value = "http://api-staging.auklet.io"
        self.assertTrue(self.client._get_kafka_certs())

    def test_write_to_local(self):
        self.client._write_to_local(self.data)
        self.assertGreater(os.path.getsize(self.client.offline_filename), 0)
        self.client._clear_file(self.client.offline_filename)

    def test_clear_file(self):
        file_name = "unit_test_temp"
        with open(file_name, "w") as unit_test_temp_file:
            unit_test_temp_file.write("data")
        self.client._clear_file(file_name)
        self.assertEqual(os.path.getsize(file_name), 0)
        os.remove(file_name)

    def test_produce_from_local(self):
        self.assertNotEqual(self.client._produce_from_local(), False)

    def test_build_usage_json(self):
        data = self.client._build_usage_json()
        for value in data.values():
            self.assertNotEqual(value, None)

    def test_update_usage_file(self):
        self.assertNotEqual(self.client._update_usage_file(), False)

    def test_check_data_limit(self):
        self.assertTrue(self.client._check_data_limit(self.data, self.client.data_current))
        self.assertTrue(self.client._check_data_limit(self.data, self.client.data_current, offline=True))
        self.client.offline_limit = self.client.data_limit = 1
        self.assertFalse(self.client._check_data_limit(self.data, self.client.data_current))
        self.client.offline_limit = self.client.data_limit = None

    def test_kafka_error_callback(self):
        self.client._kafka_error_callback(msg="", error="")
        self.assertGreater(os.path.getsize(self.client.offline_filename), 0)
        self.client._clear_file(self.client.offline_filename)

    def test_update_network_metrics(self):
        self.client.update_network_metrics(1000)
        self.assertNotEqual(self.client.system_metrics, None)
        self.client.system_metrics = None

    def test_check_date(self):
        self.assertFalse(self.client.check_date())
        self.client.data_day = 0
        self.assertFalse(self.client.check_date())
        self.client.data_day = 1

    def test_update_limits(self):
        def _get_config(self):
            return {"storage": {"storage_limit": None}, "emission_period": 60, "features": {"performance_metrics": True, "user_metrics": False}, "data": {"cellular_data_limit": None, "normalized_cell_plan_date": 1}}

        patcher = patch('auklet.base.Client._get_config', new=_get_config)
        patcher.start()
        self.assertEqual(self.client.update_limits(), 60000)
        patcher.stop()

    def test_build_event_data(self):
        def get_mock_event(exc_type=None, tb=None, tree=None, abs_path=None):
            return {"stackTrace": [{"functionName": "", "filePath": "", "lineNumber": 0, "locals": {"key": "value"}}]}

        patcher = patch('auklet.base.Event', new=get_mock_event)
        patcher.start()
        self.assertNotEqual(self.client.build_event_data(type=None, traceback="", tree=""), None)
        patcher.stop()

    def test_build_log_data(self):
        self.assertNotEqual(self.client.build_log_data(msg='msg', data_type='data_type', level='level'), None)

    # To be added if protobufs get implemented
    # def test_build_protobuf_event_data(self):
    #     def get_mock_event(exc_type=None, tb=None, tree=None, abs_path=None):
    #         return {"stackTrace": [{"functionName": "", "filePath": "", "lineNumber": 0, "locals": {"key": "value"}}]}
    #
    #     patcher = patch('auklet.base.Event', new=get_mock_event)
    #     patcher.start()
    #     self.assertNotEqual(self.client.build_protobuf_event_data(type=None, traceback="", tree=""), None)
    #     patcher.stop()
    #
    # def test_build_protobuf_log_data(self):
    #     self.assertNotEqual(self.client.build_protobuf_log_data(msg='msg', data_type='data_type', level='level'), None)

    def test__produce(self):
        pass

    def test_produce(self):
        self.client.produce(self.data)


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

    def test_stop(self):
        self.runnable._running = None
        self.assertRaises(RuntimeError, lambda: self.runnable.stop())

    def test_run(self):
        self.assertTrue(self.run())


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

    def test_get_abs_path(self):
        path = os.path.abspath(__file__)
        self.assertEqual(get_abs_path(path + "/.auklet"), path)

    def test_get_device_ip(self):
        self.assertNotEqual(get_device_ip(), None)

    def test_setup_thread_excepthook(self):
        setup_thread_excepthook()


if __name__ == '__main__':
    unittest.main()
