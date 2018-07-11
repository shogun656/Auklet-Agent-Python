import unittest

from auklet.monitoring.logging import AukletLogging


class TestAukletLogging(unittest.TestCase):
    def setUp(self):
        self.auklet_logging = AukletLogging()

    def test_log(self):
        self.assertRaises(
            NotImplementedError, lambda: self.auklet_logging.log(
                msg="", data_type=str))

    def test_debug(self):
        self.assertRaises(
            NotImplementedError, lambda: self.auklet_logging.debug(
                msg="", data_type=str))

    def test_info(self):
        self.assertRaises(
            NotImplementedError, lambda: self.auklet_logging.info(
                msg="", data_type=str))

    def test_warning(self):
        self.assertRaises(
            NotImplementedError, lambda: self.auklet_logging.warning(
                msg="", data_type=str))

    def test_error(self):
        self.assertRaises(
            NotImplementedError, lambda: self.auklet_logging.error(
                msg="", data_type=str))

    def test_critical(self):
        self.assertRaises(
            NotImplementedError, lambda: self.auklet_logging.critical(
                msg="", data_type=str))


if __name__ == '__main__':
    unittest.main()
