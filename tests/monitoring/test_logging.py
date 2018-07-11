import unittest

from auklet.monitoring.logging import AukletLogging


class TestAukletLogging(unittest.TestCase):
    def setUp(self):
        self.auklet_logging = AukletLogging()

    def test_log(self, level='INFO'):
        _ = level
        try:
            self.auklet_logging.log(msg='Log message', data_type=str)
        except NotImplementedError as error:
            self.assertEqual(str(error), 'Must implement method: log')

    def test_debug(self):
        self.test_log('DEBUG')

    def test_info(self):
        self.test_log('INFO')

    def test_warning(self):
        self.test_log('WARNING')

    def test_error(self):
        self.test_log('ERROR')

    def test_critical(self):
        self.test_log('CRITICAL')


if __name__ == '__main__':
    unittest.main()
