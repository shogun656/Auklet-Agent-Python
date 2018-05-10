# Portions of this file are taken from
# https://github.com/what-studio/profiling/tree/0.1.1,
# the license for which can be found in the "licenses/profiling.txt" file
# in this repository/package.
from __future__ import absolute_import

import time

from auklet.base import Runnable, frame_stack, Client, get_mac
from auklet.stats import MonitoringTree
from auklet.monitoring.sampling import AukletSampler


__all__ = ['MonitoringBase', 'Monitoring']


class MonitoringBase(Runnable):
    """The base class for monitoring."""

    def start(self):
        self._cpu_time_started = time.clock()
        self._wall_time_started = time.time()
        return super(MonitoringBase, self).start()

    def frame_stack(self, frame):
        return frame_stack(frame)

    def result(self):
        """Gets the frozen statistics to serialize by Pickle."""
        try:
            cpu_time = max(0, time.clock() - self._cpu_time_started)
            wall_time = max(0, time.time() - self._wall_time_started)
        except AttributeError:
            cpu_time = wall_time = 0.0
        return 0, cpu_time, wall_time


class Monitoring(MonitoringBase):
    #: The frames sampler.  Usually it is an instance of :class:`profiling.
    #: sampling.samplers.Sampler`
    sampler = None
    tree = None

    def __init__(self, apikey=None, app_id=None,
                 base_url="https://api.auklet.io/"):
        self.mac_hash = get_mac()
        client = Client(apikey, app_id, base_url, self.mac_hash)
        self.tree = MonitoringTree(self.mac_hash)
        sampler = AukletSampler(client, self.tree)
        super(Monitoring, self).__init__()
        self.sampler = sampler

    def sample(self, frame, event):
        """Samples the given frame."""
        increment_call = False
        if event == "call":
            increment_call = True
        stack = [(frame, increment_call)]
        frame = frame.f_back
        while frame:
            stack.append((frame, False))
            frame = frame.f_back
        self.tree.update_hash(stack)

    def run(self):
        self.sampler.start(self)
        yield
        self.sampler.stop()
