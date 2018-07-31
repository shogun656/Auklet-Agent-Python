import os
import unittest

from mock import patch

from auklet.utils import *
from auklet.monitoring.processing import Client
from auklet.errors import AukletConfigurationError

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import HTTPError


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.client = Client(
            apikey="", app_id="", base_url="https://api-staging.auklet.io/")

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
            build_url(self.client.base_url, extension),
            self.client.base_url + extension)

    def test_open_auklet_url(self):
        url = self.client.base_url + "private/devices/config/"
        self.assertRaises(
            AukletConfigurationError,
            lambda: open_auklet_url(url, self.client.apikey))
        url = "http://google.com/"
        self.assertNotEqual(open_auklet_url(url, self.client.apikey), None)

    def test_clear_file(self):
        file_name = "unit_test_temp"
        with open(file_name, "w") as unit_test_temp_file:
            unit_test_temp_file.write("data")
        clear_file(file_name)
        self.assertEqual(os.path.getsize(file_name), 0)
        os.remove(file_name)

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
        with patch('auklet.utils.get_ip') as mock_error:
            mock_error.side_effect = HTTPError
            self.assertIsNone(get_device_ip())
            mock_error.side_effect = Exception
            self.assertIsNone(get_device_ip())

    def test_setup_thread_excepthook(self):
        pass


if __name__ == '__main__':
    unittest.main()
