import os
import unittest
from mock import patch

from tests import data_factory

from auklet.stats import Function, Event, MonitoringTree, SystemMetrics


class TestFunction(unittest.TestCase):
    def get_test_child(self):
        class TestChild:
            func_name = "test_child"
            file_path = "file_path"
        return TestChild

    def setUp(self):
        self.function = Function(line_num=0, func_name="UnitTest")

    def test___str__(self):
        self.assertNotEqual(self.function.__str__(), None)

    def test___iter__(self):
        for t in self.function.__iter__():
            self.assertNotEqual(t, None)

    def test_has_child(self):
        self.assertFalse(self.function.has_child(test_child=""))
        self.function.children.append(self.get_test_child())
        self.assertNotEqual(
            self.function.has_child(test_child=self.get_test_child()), False)


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
        self.patcher = patch(
            'auklet.stats.MonitoringTree.get_filename', new=self.get_filename)
        self.patcher.start()
        self.event = Event(
            exc_type=str, tb=self.get_traceback(),
            tree=self.tree, abs_path="abs_path")

    def tearDown(self):
        self.patcher.stop()

    def test___iter__(self):
        for t in self.event.__iter__():
            self.assertNotEqual(t, None)

    def test_filter_frame(self):
        self.assertTrue(self.event._filter_frame(file_name="auklet"))
        self.assertFalse(self.event._filter_frame(file_name=""))

    def test_convert_locals_to_string(self):
        self.assertNotEqual(
            self.event._convert_locals_to_string(
                local_vars={"key": "value"}), None)
        self.assertNotEqual(
            self.event._convert_locals_to_string(
                local_vars={"key": True}), None)

    def test_build_traceback(self):
        def _filter_frame(self, file_name):
            _ = file_name
            return True

        with patch('auklet.stats.Event._filter_frame', new=_filter_frame):
            self.event._build_traceback(
                trace=self.get_traceback(), tree=self.tree)
            self.assertEqual(self.event.trace, [])

        def _filter_frame(self, file_name):
            _ = file_name
            return False

        with patch('auklet.stats.Event._filter_frame', new=_filter_frame):
            self.event._build_traceback(
                trace=self.get_traceback(), tree=self.tree)
            self.assertEqual(self.event.trace,
                             [{'functionName': None,
                               'filePath': '',
                               'lineNumber': 0,
                               'locals': {'key': 'value'}}])

        def get_filename(self, f_code, frame):
            _ = f_code
            _ = frame
            return "abs_path"
        with patch('auklet.stats.MonitoringTree.get_filename',
                   new=get_filename):
            self.event._build_traceback(
                trace=self.get_traceback(), tree=self.tree)
            self.assertEqual(self.event.trace,
                             [{'functionName': None,
                               'filePath': '',
                               'lineNumber': 0,
                               'locals': {'key': 'value'}}])


class TestMonitoringTree(unittest.TestCase):
    def get_code(self):
        class Code:
            co_code = "file_name"
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
        return {'callees': [],
                'filePath': None,
                'functionName': 'root',
                'lineNumber': 1,
                'nCalls': 1,
                'nSamples': 1}

    def get_parent(self):
        pass

    def get_new_parent(self):
        class Parent:
            children = []
        return Parent

    def setUp(self):
        self.monitoring_tree = MonitoringTree()
        self.function = Function(line_num=0, func_name="UnitTest")

    def test_get_filename(self):
        self.monitoring_tree.cached_filenames.clear()
        self.monitoring_tree.cached_filenames['file_name'] = "file_name"
        self.assertEqual(
            self.monitoring_tree.get_filename(
                code=self.get_code(), frame="frame"), self.get_code().co_code)

    def test_create_frame_function(self):
        self.assertNotEqual(
            self.monitoring_tree._create_frame_func(
                frame=self.get_frame()), None)

    def test_filter_frame(self):
        self.assertTrue(self.monitoring_tree._filter_frame(file_name=None))
        self.assertFalse(self.monitoring_tree._filter_frame(file_name=""))
        self.assertTrue(
            self.monitoring_tree._filter_frame(file_name="site-packages"))

    def test__build_tree(self):
        class Frame:
            class Code:
                co_code = ""
                co_firstlineno = 0
                co_name = ""
            f_code = Code()
        frame = Frame()

        result = str(self.monitoring_tree._build_tree(
            new_stack=[[frame, frame]]))

        self.assertEqual(
            result, str(data_factory.StackTraceFactory()))

        def _filter_frame(self, file_name):
            return False

        with patch('auklet.stats.MonitoringTree._filter_frame',
                   new=_filter_frame):
            result = str(self.monitoring_tree._build_tree(
                new_stack=[[frame, frame]]))

            self.assertEqual(
                result, str(data_factory.SingleNestedStackTraceFactory()))

    def test_update_sample_count(self):
        self.assertTrue(
            self.monitoring_tree._update_sample_count(
                parent=None, new_parent=self.get_new_parent()))

        class Parent:
            calls = 0
            samples = 0
            def has_child(self, new_child):
                class Child:
                    calls = 0
                    samples = 0

                child = Child
                return child
        parent = Parent()

        class NewParent:
            class NewChild:
                calls = 0
            children = [NewChild]
        new_parent = NewParent()

        with self.assertRaises(AttributeError) as error:
            self.monitoring_tree._update_sample_count(
                parent=parent, new_parent=new_parent)
        self.assertEqual("type object 'NewChild' has no attribute 'children'",
                         str(error.exception))

        class Parent:
            calls = 0
            samples = 0
            def has_child(self, new_child):
                return False
        parent = Parent()

        with self.assertRaises(AttributeError) as error:
            self.monitoring_tree._update_sample_count(
                parent=parent, new_parent=new_parent)
        self.assertEqual("'Parent' object has no attribute 'children'",
                         str(error.exception))


    def test_update_hash(self):
        self.assertNotEqual(
            self.monitoring_tree.update_hash(new_stack=""), None)

        def _update_sample_count(self, parent, new_parent):
            global test_update_hash_parent
            test_update_hash_parent = parent

        self.monitoring_tree.root_func = self.function
        with patch('auklet.stats.MonitoringTree._update_sample_count',
                   new=_update_sample_count):
            self.monitoring_tree.update_hash(new_stack="")

        self.assertNotEqual(test_update_hash_parent, None)

    def test_clear_root(self):
        self.monitoring_tree.root_func = self.get_root_function()
        self.assertTrue(self.monitoring_tree.clear_root())
        self.assertEqual(self.monitoring_tree.root_func, None)

    def test_build_tree(self):
        self.monitoring_tree.root_func = self.get_root_function()
        self.assertNotEqual(
            self.monitoring_tree.build_tree(app_id="app_id"), None)


class TestSystemMetrics(unittest.TestCase):
    def setUp(self):
        self.system_metrics = SystemMetrics()

    def test_update_network(self):
        self.system_metrics.update_network(interval=1)
        self.assertNotEqual(self.system_metrics.prev_inbound, 0)


if __name__ == '__main__':
    unittest.main()
