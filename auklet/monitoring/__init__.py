# Portions of this file are taken from
# https://github.com/what-studio/profiling/tree/0.1.1,
# the license for which can be found in the "licenses/profiling.txt" file
# in this repository/package.
from __future__ import absolute_import

import sys
import time
import signal
from six import iteritems
from six.moves import _thread

from auklet.base import Runnable, frame_stack, get_mac, setup_thread_excepthook
from auklet.monitoring.processing import ProcessingThread
# from auklet.monitoring.sampling import AukletSampler
from auklet.monitoring.logging import AukletLogging

try:
    # For Python 3.0 and later
    from multiprocessing import Queue
except ImportError:
    # Fall back to Python 2's urllib2
    from multiprocessing import Queue


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


class Monitoring(MonitoringBase, AukletLogging):
    #: The frames sampler.  Usually it is an instance of :class:`profiling.
    #: sampling.samplers.Sampler`
    sampler = None
    monitor = True
    samples_taken = 0

    def __init__(self, apikey=None, app_id=None,
                 base_url="https://api.auklet.io/", monitoring=True):
        sys.excepthook = self.handle_exc
        setup_thread_excepthook()
        self.queue = Queue(maxsize=0)
        self.mac_hash = get_mac()
        self.client = ProcessingThread(apikey, app_id, base_url,
                                       self.mac_hash)
        # sampler = AukletSampler(self.processing)
        super(Monitoring, self).__init__()
        # self.sampler = sampler
        self.monitor = monitoring

        self.interval = 0.01
        timer, sig = signal.ITIMER_REAL, signal.SIGALRM
        signal.signal(sig, self.sample)
        signal.siginterrupt(sig, False)

    def start(self):
        signal.setitimer(signal.ITIMER_PROF, self.interval, self.interval)

    def sample(self, sig, current_frame):
        """Samples the given frame."""
        current_tid = _thread.get_ident()
        for tid, frame in iteritems(sys._current_frames()):
            if tid == current_tid:
                frame = current_frame
            frames = []
            while frame is not None:
                code = frame.f_code
                frames.append((code.co_filename, frame.f_lineno, code.co_name))
                frame = frame.f_back
        self.samples_taken += 1

    def handle_exc(self, type, value, traceback):
        event = self.client.build_event_data(type, traceback)
        self.client.produce(event, "event")
        return sys.__excepthook__(type, value, traceback)

    # def log(self, msg, data_type, level="INFO"):
    #     self.client.produce(
    #         self.client.build_log_data(msg, data_type, level), "event")
