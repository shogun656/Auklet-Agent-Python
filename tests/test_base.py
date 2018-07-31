import os
import ast
import unittest


from mock import patch
from datetime import datetime

from tests import data_factory

from auklet.base import Client, Runnable
from auklet.stats import MonitoringTree


class TestClient(unittest.TestCase):
    data = ast.literal_eval(str(data_factory.MonitoringDataFactory()))

    @staticmethod
    def get_mock_event(exc_type=None, tb=None, tree=None, abs_path=None):
        return {"stackTrace":
                [{"functionName": "",
                  "filePath": "",
                  "lineNumber": 0,
                  "locals":
                    {"key": "value"}}]}

    def traceback(self):
        class Code:
            co_code = "file_name"
            co_name = ""
        class Frame:
            f_code = Code()
            f_lineno = 0
            f_locals = ""
        class Traceback:
            tb_lineno = 0
            tb_frame = Frame()
            tb_next = None
        return Traceback

    def setUp(self):
        self.client = Client(
            apikey="", app_id="", base_url="https://api-staging.auklet.io/")
        self.monitoring_tree = MonitoringTree()

    def test___init__(self):
        class SystemMetrics(object):
            global test__init__system_metrics  # used to tell a producer exists
            test__init__system_metrics = True

        with patch('auklet.stats.SystemMetrics', new=SystemMetrics):
            self.client.__init__()
            self.assertTrue(test__init__system_metrics)  # global used here

    def test_get_config(self):
        pass

    def test_load_limits(self):
        loaded = True
        if self.client._load_limits():
            loaded = False
        self.assertTrue(loaded)

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
            self.client.check_data_limit(
                data=self.data, current_use=0, offline=True))

        self.client.data_limit = None
        self.assertTrue(
            self.client.check_data_limit(data=self.data, current_use=0))

        self.client.offline_limit = self.client.data_limit = 1
        self.assertFalse(
            self.client.check_data_limit(data=self.data, current_use=0))

        self.client.data_limit = 1000
        self.client.check_data_limit(
            data=self.data, current_use=0, offline=True)
        self.assertNotEqual(self.client.offline_current, 0)

        self.client.check_data_limit(
            data=self.data, current_use=0)
        self.assertNotEqual(self.client.data_current, 0)

        self.assertTrue(
            self.client.check_data_limit(data=self.data, current_use=0))

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

    def assertBuildEventData(self, function):
        with patch('auklet.base.Event', new=self.get_mock_event):
            self.monitoring_tree.cached_filenames["file_name"] = "file_name"
            self.assertNotEqual(
                function(
                    type=Exception,
                    traceback=self.traceback(),
                    tree=self.monitoring_tree),
                None)

    def test_build_event_data(self):
        self.assertBuildEventData(self.client.build_event_data)

    def test_build_msgpack_event_data(self):
        self.assertBuildEventData(self.client.build_msgpack_event_data)

    def assertBuildLogData(self, function):
        self.assertNotEqual(function, None)

    def test_build_log_data(self):
        self.assertBuildLogData(
            self.client.build_log_data(
                msg='msg', data_type='data_type', level='level'))

    def test_build_msgpack_log_data(self):
        self.assertBuildLogData(
            self.client.build_msgpack_log_data(
                msg='msg', data_type='data_type', level='level'))


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
            global running  # used to tell if running is true
            running = True

        with patch('auklet.base.Runnable.start', new=start):
            self.runnable.__enter__()
            self.assertTrue(running)  # global variable used here

    def test___exit__(self):
        pass


if __name__ == '__main__':
    unittest.main()
