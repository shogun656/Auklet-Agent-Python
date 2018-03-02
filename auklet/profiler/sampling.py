from __future__ import absolute_import

import os
import sys
import functools
import threading
import six.moves._thread as _thread

from auklet.base import thread_clock, deferral, Runnable


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

    def __init__(self, client, profiler_tree, *args, **kwargs):
        self.sampled_times = {}
        self.counter = 0
        self.interval = INTERVAL
        self.client = client
        self.profiler_tree = profiler_tree

    def _profile(self, profiler, frame, event, arg):
        t = thread_clock()
        thread_id = _thread.get_ident()
        sampled_at = self.sampled_times.get(thread_id, 0)
        if t - sampled_at < self.interval:
            return
        self.sampled_times[thread_id] = t
        profiler.sample(frame, event)
        self.counter += 1
        if self.counter % 1000 == 0:
            # Produce tree to kafka every second
            self.client.produce(self, self.profiler_tree.root_func.to_dict())
            self.profiler_tree.clear_root()
        if self.counter % 10000 == 0:
            self._clear_for_dead_threads()

    def _clear_for_dead_threads(self):
        for thread_id in sys._current_frames().keys():
            self.sampled_times.pop(thread_id, None)

    def run(self, profiler):
        profile = functools.partial(self._profile, profiler)
        with deferral() as defer:
            sys.setprofile(profile)
            defer(sys.setprofile, None)
            threading.setprofile(profile)
            defer(threading.setprofile, None)
            yield
