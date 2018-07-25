# Portions of this file are taken from
# https://github.com/what-studio/profiling/tree/0.1.1,
# the license for which can be found in the "licenses/profiling.txt" file
# in this repository/package.
from __future__ import absolute_import

import sys
import signal
from six import iteritems
from six.moves import _thread

from auklet.base import get_mac, setup_thread_excepthook
from auklet.monitoring.processing import Client
from auklet.monitoring.logging import AukletLogging
from auklet.stats import MonitoringTree


__all__ = ['Monitoring']


except_hook_set = False


class Monitoring(AukletLogging):
    sampler = None
    monitor = True
    samples_taken = 0
    timer = signal.ITIMER_REAL
    sig = signal.SIGALRM
    stopping = False

    total_samples = 0

    emission_rate = 60  # 10 seconds
    network_rate = 10  # 10 seconds
    hour = 3600  # 1 hour

    def __init__(self, apikey=None, app_id=None,
                 base_url="https://api.auklet.io/", monitoring=True):
        global except_hook_set
        sys.excepthook = self.handle_exc
        if not except_hook_set:
            # ensure not attempting to set threading excepthook more than once
            setup_thread_excepthook()
            except_hook_set = True
        self.app_id = app_id
        self.mac_hash = get_mac()
        self.tree = MonitoringTree(self.mac_hash)
        self.client = Client(apikey, app_id, base_url, self.mac_hash, self.tree)
        self.monitor = monitoring
        self.interval = 0.01
        signal.signal(self.sig, self.sample)
        signal.siginterrupt(self.sig, False)
        super(Monitoring, self).__init__()

    def start(self):
        # Set a timer which fires a SIGALRM every .01s
        signal.setitimer(self.timer, self.interval, self.interval)

    def stop(self):
        self.stopping = True

    def sample(self, sig, current_frame):
        """Samples the given frame."""
        if self.stopping:
            signal.setitimer(self.timer, 0, 0)
            return
        current_thread = _thread.get_ident()
        for thread_id, frame in iteritems(sys._current_frames()):
            if thread_id == current_thread:
                frame = current_frame
            frames = []
            while frame is not None:
                frames.append(frame)
                frame = frame.f_back
            self.tree.update_hash(frames)
        self.total_samples += 1
        self.samples_taken += 1
        sample_timer = self.total_samples * self.interval
        if sample_timer % self.emission_rate == 0:
            tree = self.tree.build_tree(self.app_id)
            self.tree.clear_root()
            self.client.produce(tree)
            self.samples_taken = 0
        if sample_timer % self.network_rate == 0:
            self.client.update_network_metrics(self.network_rate)
        if sample_timer % self.hour == 0:
            self.emission_rate = self.client.update_limits()
            self.client.check_date()

    def handle_exc(self, type, value, traceback):
        event = self.client.build_event_data(type, traceback)
        self.client.produce(event, "event")
        sys.__excepthook__(type, value, traceback)

    def log(self, msg, data_type, level="INFO"):
        self.client.produce(
            self.client.build_log_data(msg, data_type, level), "event")
