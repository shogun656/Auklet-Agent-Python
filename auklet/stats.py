# -*- coding: utf-8 -*-
"""
   profiling.stats
   ~~~~~~~~~~~~~~~

   Statistics classes.

   :copyright: (c) 2014-2017, What! Studio
   :license: BSD, see LICENSE for more details.

"""
from __future__ import absolute_import, division

import json
import inspect
import pprint

dict()
__all__ = ['AukletProfileTree']


class Function(object):
    root = False
    samples = 1
    calls = 0
    line_num = ''
    func_name = ''
    file_name = ''

    children = []
    parent = None

    def __init__(self, line_num, func_name, file_name, root=False,
                 parent=None, calls=0):
        self.line_num = line_num
        self.func_name = func_name
        self.file_name = file_name
        self.root = root
        self.parent = parent
        self.children = []
        self.calls = calls

    def __str__(self):
        pp = pprint.PrettyPrinter()
        return pp.pformat(self.to_dict())

    def to_dict(self):
        return {
            "root": self.root,
            "fileName": self.file_name,
            "funcName": self.func_name,
            "nSamples": self.samples,
            "lineNum": self.line_num,
            "nCalls": self.calls,
            "callees": [item.to_dict() for item in self.children]
        }

    def has_child(self, test_child):
        for child in self.children:
            if test_child.func_name == child.func_name \
                    and test_child.file_name == child.file_name:
                return child
        return False


class AukletProfileTree(object):
    root_func = None

    def _create_frame_func(self, frame, root=False, parent=None):
        if root:
            return Function(
                line_num=1,
                func_name="root",
                file_name="root",
                root=True,
                parent=None,
                calls=1
            )

        calls = 0
        if frame[1]:
            calls = 1
        frame = frame[0]
        return Function(
            line_num=frame.f_lineno,
            func_name=frame.f_code.co_name,
            file_name=inspect.getsourcefile(frame) or inspect.getfile(frame),
            root=root,
            parent=parent,
            calls=calls
        )

    def _remove_ignored_frames(self, new_stack):
        cleansed_stack = []
        for frame in new_stack:
            file_name = inspect.getsourcefile(frame[0]) or \
                        inspect.getfile(frame[0])
            if "site-packages" not in file_name:
                cleansed_stack.append(frame)
        return cleansed_stack

    def _build_tree(self, new_stack):
        new_stack = self._remove_ignored_frames(new_stack)
        root_func = self._create_frame_func(None, True)
        parent_func = root_func
        for frame in reversed(new_stack):
            current_func = self._create_frame_func(
                frame, parent=parent_func)
            parent_func.children.append(current_func)
            parent_func = current_func
        return root_func

    def _update_sample_count(self, parent, new_parent):
        if not new_parent.children:
            return True
        new_child = new_parent.children[0]
        has_child = parent.has_child(new_child)
        if has_child:
            has_child.calls += new_child.calls
            has_child.samples += 1
            return self._update_sample_count(has_child, new_child)
        parent.children.append(new_child)

    def update_hash(self, new_stack):
        new_tree_root = self._build_tree(new_stack)
        if self.root_func is None:
            self.root_func = new_tree_root
            return self.root_func
        self.root_func.samples += 1
        self._update_sample_count(self.root_func, new_tree_root)
        print self.root_func.to_dict()

    def clear_root(self):
        self.root_func = None
        return True
