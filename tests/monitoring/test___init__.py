import unittest
from mock import patch

from auklet.monitoring import Monitoring


class TestMonitoring(unittest.TestCase):
    def setUp(self):
        def _get_certs(self):
            return True
        self.patcher = patch(
            'auklet.broker.KafkaClient._get_certs', new=_get_certs)
        self.patcher.start()
        self.monitoring = Monitoring(
            apikey="",
            app_id="",
            base_url="https://api-staging.io",
            monitoring=True)
        self.monitoring.monitor = True

    def tearDown(self):
        self.patcher.stop()

    def test_start(self):
        self.monitoring.start()
        self.assertTrue(self.monitoring.monitor)
        self.monitoring.stop()
        self.monitoring.monitor = False

    def build_assert_equal(self, expected):
        self.assertEqual(
            expected, str(test_sample_stack[0]).strip(')').split(", ")[-1])

    def test_sample(self):
        class CoCode:
            co_code = None
            co_firstlineno = None
            co_name = None
        class FBack:
            f_back = None
            f_code = CoCode()
        class Frame:
            f_back = FBack()
            f_code = CoCode()

        def update_hash(self, stack):
            global test_sample_stack  # used to tell if stack was created
            test_sample_stack = stack

        with patch('auklet.stats.MonitoringTree.update_hash', new=update_hash):
            self.monitoring.sample(None, current_frame=Frame())
            self.assertIsNotNone(test_sample_stack)
            self.monitoring.sample(None, current_frame=Frame())
            self.assertTrue(test_sample_stack)  # global used here
            self.build_assert_equal("True")
            self.monitoring.sample(None, current_frame=Frame())
            self.build_assert_equal("True")

    def test_log(self):
        self.assertEqual(self.monitoring.log(msg="msg", data_type="str"), None)


if __name__ == '__main__':
    unittest.main()
