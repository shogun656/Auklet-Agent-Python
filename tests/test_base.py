import io
import os
import sys
import ast
import json
import msgpack
import unittest
import zipfile

from mock import patch
from datetime import datetime
from kafka.errors import KafkaError
from ipify.exceptions import IpifyException

from tests import data_factory

from auklet import base
from auklet.base import *
from auklet.stats import MonitoringTree
from auklet.errors import AukletConfigurationError

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError, URLError

class TestClient(unittest.TestCase):
    data = ast.literal_eval(str(data_factory.MonitoringDataFactory()))
    config = ast.literal_eval(str(data_factory.ConfigFactory()))

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
        def _get_kafka_brokers(self):
            self.brokers = ["http://api-staging.auklet.io:9093"]
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
        self.patcher.stop()

    def base_patch_side_effect_with_none(self, location, side_effect, actual):
        with patch(location) as _base:
            _base.side_effect = side_effect
            self.assertIsNone(actual)


    def test___init__(self):
        if sys.version_info < (3,):
            pass
        else:
            with patch('auklet.base.Client._get_kafka_brokers') \
                    as _get_kafka_brokers:
                _get_kafka_brokers.return_value = True
                with patch('auklet.base.Client._get_kafka_certs') \
                        as _get_kafka_certs:
                    _get_kafka_certs.return_value = True
                    self.base_patch_side_effect_with_none(
                        'auklet.base', KafkaError, self.client.__init__())



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

        with patch('auklet.base.urlopen') as url_open:
            self.assertIsNotNone(self.client._open_auklet_url(url))

            url_open.side_effect = HTTPError(
                url=None, code=401, msg=None, hdrs=None, fp=None)
            self.assertRaises(AukletConfigurationError,
                              lambda: self.client._open_auklet_url(url))

            url_open.side_effect = HTTPError(
                url=None, code=None, msg=None, hdrs=None, fp=None)
            self.assertRaises(HTTPError,
                              lambda: self.client._open_auklet_url(url))

    def test_get_config(self):
        with patch('auklet.base.Client._open_auklet_url') as _open_auklet_url:
            with patch('auklet.base.u') as u:
                u.return_value = """{"config": "data"}"""
                _open_auklet_url.return_value = urlopen(
                    "http://api-staging.auklet.io")
                self.assertEqual("data", self.client._get_config())

    def test_get_kafka_brokers(self):
        filename = self.client.com_config_filename
        with open(filename, "w") as config:
            config.write(json.dumps(self.config))

        with patch('auklet.base.Client._open_auklet_url') as _open_auklet_url:
            _open_auklet_url.return_value = None
            self.assertTrue(self.client._get_kafka_brokers())
            open(filename, "w").close()

            with patch('auklet.base.u') as u:
                u.return_value = str(data_factory.ConfigFactory())
                _open_auklet_url.return_value = urlopen(
                    "http://api-staging.auklet.io")
                self.client._get_kafka_brokers()
                self.assertEqual(
                    ['http://api-staging.auklet.io:9093'],
                    self.client.brokers)
                self.assertEqual(
                    {'monitoring': 'profiling',
                     'event': 'events',
                     'log': 'logging'},
                    self.client.producer_types)

    def test_write_kafka_conf(self):
        filename = self.client.com_config_filename
        self.client._write_kafka_conf(info=self.config)
        self.assertGreater(os.path.getsize(filename), 0)
        open(filename, "w").close()

    def build_test_load_kafka_conf(self, file):
        with patch(file) as _file:
            _file.side_effect = OSError
            self.assertFalse(self.client._load_kafka_conf())

    def test_load_kafka_conf(self):
        filename = self.client.com_config_filename
        with open(filename, "w") as config:
            config.write(json.dumps(self.config))
        self.assertTrue(self.client._load_kafka_conf())
        open(filename, "w").close()

        if sys.version_info < (3,):
            self.build_test_load_kafka_conf("__builtin__.open")
        else:
            self.build_test_load_kafka_conf("builtins.open")


    def build_load_limits_test(self, expected, actual):
        self.assertEqual(expected, actual)

    def write_load_limits_test(self, data):
        filename = self.client.limits_filename
        with open(filename, "w") as limits:
            limits.write(str(data))

    def test_load_limits(self):
        default_data = data_factory.LimitsGenerator()
        self.write_load_limits_test(default_data)
        self.build_load_limits_test(1, self.client.data_day)

        self.assertEqual(None, self.client.data_limit)
        self.assertEqual(None, self.client.offline_limit)

        data = data_factory.LimitsGenerator(cellular_data_limit=10)
        self.write_load_limits_test(data)
        self.client._load_limits()
        self.build_load_limits_test(10000000.0, self.client.data_limit)

        data = data_factory.LimitsGenerator(
            cellular_data_limit="null", storage_limit=10)
        self.write_load_limits_test(data)
        self.client._load_limits()
        self.build_load_limits_test(10000000.0, self.client.offline_limit)

        with open(self.client.limits_filename, "w") as limits:
            limits.write(str(default_data))

        self.base_patch_side_effect_with_none(
            'auklet.base.open', IOError, self.client._load_limits())

    def test_get_kafka_certs(self):
        self.assertFalse(self.client._get_kafka_certs())

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
                    self.assertTrue(self.client._get_kafka_certs())

        else:
            with patch('auklet.base.Request') as _request:
                _request.return_value = "http://api-staging.auklet.io"
                with patch('auklet.base.urlopen') as _urlopen:
                    _urlopen.side_effect = urlopen
                    self.assertTrue(self.client._get_kafka_certs())

    def recreate_files(self):
        os.system("touch .auklet/version")
        os.system("touch .auklet/communication")
        os.system("touch .auklet/usage")
        os.system("touch .auklet/limits")

    def test_write_to_local(self):
        open(self.client.offline_filename, "w").close()
        if sys.version_info < (3,):
            self.client._write_to_local(data=self.data, data_type="event")
        else:
            self.client._write_to_local(data=msgpack.packb(self.data), data_type="")
        self.assertGreater(os.path.getsize(self.client.offline_filename), 0)
        self.client._clear_file(self.client.offline_filename)

        os.system("rm -R .auklet")
        self.assertFalse(self.client._write_to_local(self.data, data_type=""))
        os.system("mkdir .auklet")
        os.system("touch %s" % self.client.offline_filename)
        self.recreate_files()


    def test_clear_file(self):
        file_name = "unit_test_temp"
        with open(file_name, "w") as unit_test_temp_file:
            unit_test_temp_file.write("data")
        self.client._clear_file(file_name)
        self.assertEqual(os.path.getsize(file_name), 0)
        os.remove(file_name)

    def test_produce_from_local(self):
        open(self.client.offline_filename, "w").close()
        def _produce(self, data, data_type):
            global test_produced_data  # used to tell data was produced
            test_produced_data = data

        with patch('auklet.base.Client._produce', new=_produce):
            with open(self.client.offline_filename, "a") as offline:
                offline.write("event::")
                if sys.version_info < (3,):
                    offline.write(str(self.data))
                else:
                    offline.write(str(msgpack.packb(self.data)))
                offline.write("\n")
            self.client._produce_from_local()
        self.assertIsNotNone(test_produced_data)  # global used here
        os.system("rm -R .auklet")
        self.assertFalse(self.client._produce_from_local())
        os.system("mkdir .auklet")
        os.system("touch %s" % self.client.offline_filename)
        self.recreate_files()

    def test_build_usage_json(self):
        data = self.client._build_usage_json()
        for value in data.values():
            self.assertNotEqual(value, None)

    def test_update_usage_file(self):
        os.system("rm -R .auklet")
        self.assertFalse(self.client._update_usage_file())
        os.system("mkdir .auklet")
        os.system("touch %s" % self.client.offline_filename)
        self.recreate_files()

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
        self.client._kafka_error_callback(msg="", error="", data_type="")
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

    def test_update_limits(self):
        global none                 # Global variables are needed due to mock
        global cellular_data_limit  # functions not being able to accept
        global storage_limit        # different variables in the new function
        global cell_plan_date

        none = True
        cellular_data_limit = None
        storage_limit = None
        cell_plan_date = 1

        with patch('auklet.base.Client._get_config', new=self._get_config):
            self.assertEqual(self.client.update_limits(), 60)
            none = False

            cellular_data_limit = storage_limit = 1000
            cell_plan_date = 10
            self.client.update_limits()
            self.assertEqual(self.client.data_limit, 1000000000.0)
            self.assertEqual(self.client.offline_limit, 1000000000.0)
            self.assertEqual(self.client.data_day, 10)
            cellular_data_limit = storage_limit = None
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

    def test__produce(self):
        class KafkaProducer:
            def __init__(self, **configs):
                pass

            def send(self, data_type, value, key):
                global test__produce_value
                test__produce_value = value

        with patch('kafka.KafkaProducer', new=KafkaProducer):
            self.client.producer = KafkaProducer()
            self.assertRaises(
                AttributeError, lambda: self.client._produce(data=self.data))
            self.assertEqual(self.data, test__produce_value)

    def _produce(self, data, data_type="monitoring"):
        global test_produce_data  # used to tell data was produced
        test_produce_data = data

    def _check_data_limit(self, data, data_current, offline=False):
        if not error or offline:  # global used here
            return True
        else:
            raise KafkaError

    def test_produce(self):
        global error  # used to tell which test case is being tested
        error = False

        def _produce(self, data, data_type="monitoring"):
            global test_produce_data  # used to tell data was produced
            test_produce_data = data

        def _check_data_limit(self, data, data_current, offline=False):
            if not error or offline:  # global used here
                return True
            else:
                raise KafkaError

        with patch('auklet.base.Client._produce', new=_produce):
            with patch('auklet.base.Client._check_data_limit',
                       new=_check_data_limit):
                self.client.producer = True
                with open(self.client.offline_filename, "w") as offline:
                    offline.write("event::")
                    if sys.version_info < (3,):
                        offline.write(str(self.data))
                    else:
                        offline.write(str(msgpack.packb(self.data)))
                    offline.write("\n")
                self.client.produce(self.data)
                self.assertNotEqual(
                    str(test_produce_data), None)  # global used here
                error = True
                self.client.produce(self.data)
                self.assertGreater(
                    os.path.getsize(self.client.offline_filename), 0)


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

        with patch('auklet.base.Runnable.run') as _run:
            _run.return_value = True
            with patch('auklet.base.next') as _next:
                _next.return_value = True
                self.assertRaises(TypeError, lambda: self.runnable.start())

                self.runnable._running = None
                _next.side_effect = StopIteration
                self.assertRaises(TypeError, lambda: self.runnable.start())

    def test_stop(self):
        self.runnable._running = None
        self.assertRaises(RuntimeError, lambda: self.runnable.stop())
        self.runnable._running = True

        with patch('auklet.base.next') as _next:
            _next.side_effect = StopIteration
            self.assertRaises(StopIteration, self.runnable.stop())

            self.runnable._running = True
            _next.side_effect = None
            self.assertRaises(TypeError, lambda: self.runnable.stop())

    def test_run(self):
        if sys.version_info < (3,):
            self.assertIsNone(self.run())
        else:
            self.assertTrue(self.run())

    def test___enter__(self):
        def start(self):
            global running  # used to tell if running is true
            running = True

        with patch('auklet.base.Runnable.start', new=start):
            self.runnable.__enter__()
            self.assertTrue(running)  # global variable used here

    def test___exit__(self):
        self.runnable._running = True
        self.assertRaises(TypeError, lambda: self.runnable.__exit__())


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
        with patch('auklet.base.get_ip') as _get_ip:
            _get_ip.return_value = True
            self.assertNotEqual(get_device_ip(), None)
            _get_ip.side_effect = IpifyException
            self.assertIsNone(get_device_ip())
            _get_ip.side_effect = Exception
            self.assertIsNone(get_device_ip())

    def throw_exception(self):
        raise Exception

    def throw_keyboard_interrupt(self):
        raise KeyboardInterrupt

    def test_setup_thread_excepthook(self):
        print("\nDue to the nature of this test and of the function itself, "
              "the two Stack Traces, Exception and KeyboardInterrupt, "
              "must print in order to prove validity of test.")
        from threading import Thread
        self.assertIsNone(setup_thread_excepthook())
        thread_except = Thread(target=self.throw_exception)
        thread_keyboard_interrupt = \
            Thread(target=self.throw_keyboard_interrupt)
        thread_except.start()
        thread_keyboard_interrupt.start()
        os.system("sleep 2")

    def test_version_info(self):
        self.assertNotEqual(None, base.b('b'))
        self.assertNotEqual(None, base.u(b'u'))

    def test_deferral(self):
        self.assertIsNotNone(deferral())


if __name__ == '__main__':
    unittest.main()
