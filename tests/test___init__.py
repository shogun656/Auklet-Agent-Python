import unittest
from mock import patch

from auklet.monitoring import MonitoringBase, Monitoring


class TestMonitoringBase(unittest.TestCase):
    def setUp(self):
        self.monitoring_base = MonitoringBase()

    def test_start(self):
        self.assertRaises(
            NotImplementedError, lambda: self.monitoring_base.start())
        self.assertRaises(
            RuntimeError, lambda: self.monitoring_base.start())

    def test_frame_stack(self):
        class Frame:
            f_back = None
        frame = Frame()
        self.assertNotEqual(
            self.monitoring_base.frame_stack(frame=frame), None)

    def test_results(self):
        self.monitoring_base._cpu_time_started = \
            self.monitoring_base._wall_time_started = None
        self.assertRaises(TypeError, lambda: self.monitoring_base.result())
        self.monitoring_base._cpu_time_started = \
            self.monitoring_base._wall_time_started = 0
        self.assertNotEqual(str(self.monitoring_base.result()), "(0, 0, 0)")

        with patch('auklet.monitoring.max') as mock_max:
            mock_max.side_effect = AttributeError
            self.assertEqual(
                str(self.monitoring_base.result()), "(0, 0.0, 0.0)")


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
        self.assertTrue(self.monitoring.monitor)
        self.monitoring.monitor = False
        self.assertFalse(self.monitoring.monitor)
        self.monitoring.monitor = True
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
            self.monitoring.sample(frame=Frame(), event="event")
            self.assertIsNotNone(test_sample_stack)
            self.monitoring.sample(frame=Frame(), event="call")
            self.assertTrue(test_sample_stack)  # global used here
            self.build_assert_equal("True")
            self.monitoring.sample(frame=Frame, event="call")
            self.build_assert_equal("True")

    def test_run(self):
        self.monitoring.run()
        self.assertEqual(self.monitoring.sampler.start(self.monitoring), None)
        self.monitoring.sampler.stop()
        self.monitoring.sampler.start(self.monitoring)
        self.assertEqual(self.monitoring.sampler.stop(), None)

    def test_log(self):
        self.assertEqual(self.monitoring.log(msg="msg", data_type="str"), None)


if __name__ == '__main__':
    unittest.main()
