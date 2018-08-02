import unittest
from mock import patch

from auklet.monitoring import Monitoring


class TestMonitoring(unittest.TestCase):
    def setUp(self):
        self.monitoring = Monitoring(
            apikey="",
            app_id="",
            base_url="https://api-staging.io",
            monitoring=True)
        self.monitoring.monitor = True

    def test_start(self):
        self.monitoring.start()
        self.assertTrue(self.monitoring.monitor)
        self.monitoring.stop()
        self.monitoring.monitor = False

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
            self.assertTrue(test_sample_stack)

    def test_log(self):
        def new_publish():
            return True

        with patch('auklet.broker.mqtt.Client.publish', new=new_publish()):
            self.assertEqual(
                self.monitoring.log(msg="msg", data_type="str"), None)


if __name__ == '__main__':
    unittest.main()
