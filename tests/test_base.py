import os
import unittest

os.chdir("..")
from auklet.base import *
from auklet.stats import MonitoringTree

class TestClient(unittest.TestCase):
    data = """{"commitHash": "9f7ce8f9d5d55e1f9902aa1c941d93403ee97f40", "id": "ee7451a3-789e-44a2-95d7-32dbe8b069cc", "tree": {"lineNumber": 1, "nSamples": 173756, "functionName": "root", "nCalls": 1, "callees": [{"lineNumber": 1, "nSamples": 1203, "functionName": "<module>", "nCalls": 0, "callees": [{"lineNumber": 26, "nSamples": 1203, "functionName": "main", "nCalls": 0, "callees": [{"lineNumber": 12, "nSamples": 28, "functionName": "__new__", "nCalls": 7, "callees": [], "filePath": "<string>"}, {"lineNumber": 31, "nSamples": 2, "functionName": "__repr__", "nCalls": 1, "callees": [], "filePath": "<string>"}], "filePath": "vdas/vdas.py"}], "filePath": "vdas/vdas.py"}, {"lineNumber": 9, "nSamples": 166541, "functionName": "on_press", "nCalls": 0, "callees": [], "filePath": "/vdas/button.py"}, {"lineNumber": 12, "nSamples": 28, "functionName": "__new__", "nCalls": 7, "callees": [], "filePath": "<string>"}, {"lineNumber": 31, "nSamples": 4, "functionName": "__repr__", "nCalls": 2, "callees": [], "filePath": "<string>"}], "filePath": None}, "publicIP": "96.64.10.67", "timestamp": 1530555317012, "application": "tyJSjp3aSyxxdoGAtqsMT4", "macAddressHash": "be7f80c587aee80972ab1f98b8f4203c"}"""
    def setUp(self):
        self.client = Client(
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiODE2YjlkOTItYjg0Yi00OGUzLWI1ZDQtYmYwMGZiODBhOTU3IiwidXNlcm5hbWUiOiIyMjBhYzVlMy1iZGEyLTRmYmQtYTJiZi1lZDYyNWRjMGM0N2EiLCJleHAiOjE1Mjk1OTI3ODksImVtYWlsIjoiIn0.6eWsEoAnVMHkAf4Vy2-WOjxicB5KKrKBHzTFG63ZI3g",
            "jWmc4aPf5XnHHjiNbLyyNB",
            base_url="https://api-staging.auklet.io/")
        self.tree = MonitoringTree()

    def test_create_file(self):
        self.client._create_file(self.client.offline_filename)
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
        self.assertNotEqual(self.client._open_auklet_url(url), None)

    def test_get_config(self):
        self.assertNotEqual(self.client._get_config(), None)

    def test_get_kafka_brokers(self):
        self.assertEqual(self.client._get_kafka_brokers(), None)

    def test_write_kafka_conf(self):
        self.client._write_kafka_conf(info="info")
        self.assertGreater(os.path.getsize(self.client.com_config_filename), 0)
        self.client._clear_file(self.client.com_config_filename)

    def test_load_data_config(self):
        self.assertTrue(self.client._load_kafka_conf())

    def test_load_limits(self):
        loaded = True
        if self.client._load_limits():
            loaded = False
        self.assertTrue(loaded)

    def test_get_kafka_certs(self):
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
        self.client.offline_limit = self.client.data_limit = 1000
        self.assertFalse(self.client._check_data_limit(self.data, self.client.data_current))
        self.client.offline_limit = self.client.data_limit = None

    def test_kafka_error_callback(self):
        msg = "msg"
        self.client._kafka_error_callback(msg)
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
        self.assertNotEqual(self.client.update_limits(), 60)

    def test_build_event_data(self):
        class CoCode:
            co_code = {"file_name", "file_name"}

        class Frame:
            f_code = CoCode()

        class Traceback:
            tb_lineno = 0
            tb_frame = Frame()

        class Tree:
            get_filename = 0

        tb = Traceback()

        try:
            _ = 1 / 0
        except ZeroDivisionError:
            self.client.build_event_data(ZeroDivisionError, tb, self.tree)

    def test_build_log_data(self):
        self.assertNotEqual(self.client.build_log_data(msg='msg', data_type='data_type', level='level'), None)

    def test_build_protobuf_event_data(self):
        pass

    def test_build_protobuf_log_data(self):
        self.assertNotEqual(self.client.build_protobuf_log_data(msg='msg', data_type='data_type', level='level'), None)

    def test__produce(self):
        pass

    def test_produce(self):
        pass

class TestRunnable(unittest.TestCase):
    def setUp(self):
        self.runnable = Runnable()

    def test_is_running(self):
        self.assertFalse(self.runnable.is_running())
        self.runnable._running = 1
        self.assertTrue(self.runnable.is_running())
        self.runnable._running = None

    def test_start(self):
        pass
        # self.runnable.run()
        # self.runnable.start(None, None)
        # self.assertNotEqual(self.runnable._running, None)

    def test_stop(self):
        pass

    def test_run(self):
        pass

class Test(unittest.TestCase):
    def test_frame_stack(self):
        pass
        # self.assertNotEqual(frame_stack(frame="frame"), None)

    def test_get_mac(self):
        self.assertNotEqual(get_mac(), None)

    def test_get_commit_hash(self):
        self.assertNotEqual(get_commit_hash(), "")

    def test_get_abs_path(self):
        path = os.path.abspath(__file__)
        self.assertEqual(get_abs_path(path + "/.auklet"), path)

    def test_get_device_ip(self):
        self.assertNotEqual(get_device_ip(), None)

    def test_setup_thread_excepthook(self):
        pass
