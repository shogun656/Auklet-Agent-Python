import string
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



class TestMonitoring(unittest.TestCase):
    def setUp(self):
        self.function = Monitoring(
            apikey="",
            app_id="",
            base_url="https://api-staging.io",
            monitoring=True)

    def test_start(self):
        self.assertTrue(self.function.monitor)
        self.function.monitor = False
        self.assertFalse(self.function.monitor)
        self.function.monitor = True

    def test_sample(self):
        class CoCode:
            co_code = None
            co_firstlineno = None
            co_name = None
        class Frame:
            f_back = None
            f_code = CoCode()
        frame = Frame()

        def update_hash(self, stack):
            global test_sample_stack
            test_sample_stack = stack

        with patch('auklet.stats.MonitoringTree.update_hash', new=update_hash):
            self.function.sample(frame=frame, event="event")
            self.assertEqual(
                str(test_sample_stack[0]).strip(')').split(", ")[1], "False")
            self.function.sample(frame=frame, event="call")
            self.assertTrue(test_sample_stack)
            self.assertEqual(
                str(test_sample_stack[0]).strip(')').split(", ")[1], "True")

    def test_run(self):
        self.function.run()
        self.assertEqual(self.function.sampler.start(self.function), None)
        self.function.sampler.stop()
        self.function.sampler.start(self.function)
        self.assertEqual(self.function.sampler.stop(), None)

    def test_log(self):
        self.assertEqual(self.function.log(msg="msg", data_type="str"), None)


if __name__ == '__main__':
    unittest.main()
