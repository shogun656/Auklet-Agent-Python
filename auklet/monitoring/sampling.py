# Portions of this file are taken from
# https://github.com/what-studio/profiling/tree/0.1.1,
# the license for which can be found in the "licenses/profiling.txt" file
# in this repository/package.
from __future__ import absolute_import, unicode_literals

import sys
import functools
import threading
from time import time
from auklet.base import Runnable, setup_thread_excepthook, deferral


__all__ = ['AukletSampler']

INTERVAL = 1e-3  # 1ms


class AukletSampler(Runnable):
    """Uses :func:`sys.setprofile` and :func:`threading.setprofile` to sample
    running frames per thread.  It can be used at systems which do not support
    profiling signals.
    Just like :class:`profiling.tracing.timers.ThreadTimer`, `Yappi`_ is
    required for earlier than Python 3.3.
    .. _Yappi: https://code.google.com/p/yappi/
    """
    client = None
    emission_rate = 60  # 10 seconds
    network_rate = 10  # 10 seconds
    hour = 3600  # 1 hour

    def __init__(self, client, tree, *args, **kwargs):
        sys.excepthook = self.handle_exc
        self.sampled_times = {}
        self.interval = INTERVAL
        self.client = client
        self.tree = tree
        self.emission_rate = self.client.update_limits()
        self.start_time = int(time())
        self.prev_diff = 0
        setup_thread_excepthook()

    def _profile(self, profiler, frame, event, arg):
        time_diff = int(time()) - self.start_time
        profiler.sample(frame, event)
        if self.prev_diff != 0 and self.prev_diff != time_diff:
            if time_diff % (self.emission_rate / 1000) == 0:
                self.client.produce(
                    self.tree.build_tree(self.client.app_id))
                self.tree.clear_root()

            if time_diff % self.network_rate == 0:
                self.client.update_network_metrics(self.network_rate)

            if time_diff % self.hour == 0:
                self.emission_rate = self.client.update_limits()
                self.client.check_date()
        self.prev_diff = time_diff

    def handle_exc(self, type, value, traceback):
        event = self.client.build_event_data(type, traceback,
                                             self.tree)
        self.client.produce(event, "event")

    def run(self, profiler):
        profile = functools.partial(self._profile, profiler)
        with deferral() as defer:
            sys.setprofile(profile)
            defer(sys.setprofile, None)
            threading.setprofile(profile)
            defer(threading.setprofile, None)
            yield
