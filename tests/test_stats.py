import os
import unittest

os.chdir("..")
from auklet.stats import Function, Event, MonitoringTree, SystemMetrics


class TestFunction(unittest.TestCase):
    def setUp(self):
        self.function = Function(line_num=0, func_name="UnitTest")

    def test_has_child(self):
        pass
        # self.assertFalse(self.function.has_child(""))
        # self.function.children.append("Child")
        # self.function.children['Child'].func_name = "UnitTest"
        # self.function.has_child("child")


class TestEvent(unittest.TestCase):
    def setUp(self):
        pass


class TestMonitoringTree(unittest.TestCase):
    def setUp(self):
        self.monitoring_tree = MonitoringTree()

    def test_get_filename(self):
        pass
        # class Code:
        #
        #     co_code
        # code = "code"
        # code.co_code = "co_code"
        # self.monitoring_tree.get_filename(code=code, frame="frame")


class TestSystemMetrics(unittest.TestCase):
    def setUp(self):
        self.system_metrics = SystemMetrics()

    def test_update_network(self):
        pass