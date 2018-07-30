import os
import ast
import json
import msgpack
import unittest


from mock import patch
from datetime import datetime
from kafka.errors import KafkaError
from ipify.exceptions import IpifyException

from tests import data_factory

from auklet.base import Client
from auklet.utils import *
from auklet.errors import AukletConfigurationError

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
