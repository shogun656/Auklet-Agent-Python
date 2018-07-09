import os
import unittest
from mock import patch

os.chdir("..")
from auklet.stats import Function, Event, MonitoringTree, SystemMetrics
from auklet.protobuf import data_pb2


class TestFunction(unittest.TestCase):
    def get_test_child(self):
        class TestChild:
            func_name = "test_child"
            file_path = "file_path"
        return TestChild

    def setUp(self):
        self.function = Function(line_num=0, func_name="UnitTest")

    def test_has_child(self):
        self.assertFalse(self.function.has_child(test_child=""))
        self.function.children.append(self.get_test_child())
        self.assertNotEqual(self.function.has_child(test_child=self.get_test_child()), False)


class TestEvent(unittest.TestCase):
    def get_filename(self, code="code", frame="frame"):
        _ = code
        _ = frame
        return ""

    def get_traceback(self):
        class Code:
            co_name = None
        class Frame:
            f_code = Code()
            f_lineno = 0
            f_locals = {"key": "value"}
        class Traceback:
            tb_lineno = 0
            tb_frame = Frame()
            tb_next = None
        return Traceback

    def setUp(self):
        self.tree = MonitoringTree()
        patcher = patch('auklet.stats.MonitoringTree.get_filename', new=self.get_filename)
        patcher.start()
        self.event = Event(exc_type=str, tb=self.get_traceback(), tree=self.tree, abs_path="abs_path")

    def test_filter_frame(self):
        self.assertTrue(self.event._filter_frame(file_name="auklet"))
        self.assertFalse(self.event._filter_frame(file_name=""))

    def test_convert_locals_to_string(self):
        self.assertNotEqual(self.event._convert_locals_to_string(local_vars={"key": "value"}), None)

    def test_build_traceback(self):
        self.assertEqual(self.event._build_traceback(trace=self.get_traceback(), tree=self.tree), None)


class TestMonitoringTree(unittest.TestCase):
    def get_code(self):
        class Code:
            co_code = "name"
            co_firstlineno = 0
            co_name = ""
        return Code

    def get_frame(self):
        class Frame:
            f_code = self.get_code()
        frame = []
        frame.append(Frame)
        frame.append(Frame)
        return frame

    def get_root_function(self):
        return {'callees': [], 'filePath': None, 'functionName': 'root', 'lineNumber': 1, 'nCalls': 1, 'nSamples': 1}

    def get_parent(self):
        pass

    def get_new_parent(self):
        class Parent:
            children = []
        return Parent

    def setUp(self):
        self.monitoring_tree = MonitoringTree()

    def test_get_filename(self):
        file = "contents_of_file"
        self.monitoring_tree.cached_filenames.clear()
        self.monitoring_tree.cached_filenames['name'] = file
        self.assertTrue(self.monitoring_tree.get_filename(code=self.get_code(), frame="frame"), file)

    def test_create_frame_function(self):
        self.assertNotEqual(self.monitoring_tree._create_frame_func(frame=self.get_frame()), None)

    def test_filter_frame(self):
        self.assertTrue(self.monitoring_tree._filter_frame(file_name=None))
        self.assertFalse(self.monitoring_tree._filter_frame(file_name=""))
        self.assertTrue(self.monitoring_tree._filter_frame(file_name="site-packages"))

    def test__build_tree(self):
        self.assertNotEqual(self.monitoring_tree._build_tree(new_stack=""), None)

    def test_build_protobuf_tree(self):
        self.protobuf_monitoring_data = data_pb2.ProtobufMonitoringData()
        self.assertNotEqual(self.monitoring_tree._build_protobuf_tree(root_tree=self.get_root_function(), message=self.protobuf_monitoring_data), None)

    def test_build_protobuf_monitoring_data(self):
        self.monitoring_tree.root_func = self.get_root_function()
        self.assertNotEqual(self.monitoring_tree.build_protobuf_monitoring_data(app_id="app_id"), None)

    def test_update_sample_count(self):
        self.assertTrue(self.monitoring_tree._update_sample_count(parent=None, new_parent=self.get_new_parent()))

    def test_update_hash(self):
        self.assertNotEqual(self.monitoring_tree.update_hash(new_stack=""), None)

    def test_clear_root(self):
        self.monitoring_tree.root_func = self.get_root_function()
        self.assertTrue(self.monitoring_tree.clear_root())
        self.assertEqual(self.monitoring_tree.root_func, None)

    def test_build_tree(self):
        self.monitoring_tree.root_func = self.get_root_function()
        self.assertNotEqual(self.monitoring_tree.build_tree(app_id="app_id"), None)


class TestSystemMetrics(unittest.TestCase):
    def setUp(self):
        self.system_metrics = SystemMetrics()

    def test_update_network(self):
        self.system_metrics.update_network(interval=1)
        self.assertNotEqual(self.system_metrics.prev_inbound, 0)
