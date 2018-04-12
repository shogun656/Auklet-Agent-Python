from __future__ import absolute_import

import sys
import functools
import threading
import six.moves._thread as _thread

from auklet.base import thread_clock, deferral, Runnable, setup_thread_excepthook


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

    def __init__(self, client, tree, *args, **kwargs):
        sys.excepthook = self.handle_exc
        self.sampled_times = {}
        self.counter = 0
        self.interval = INTERVAL
        self.client = client
        self.tree = tree
        setup_thread_excepthook()

    def _profile(self, profiler, frame, event, arg):
        t = thread_clock()
        thread_id = _thread.get_ident()
        sampled_at = self.sampled_times.get(thread_id, 0)
        if t - sampled_at < self.interval:
            return
        self.sampled_times[thread_id] = t
        profiler.sample(frame, event)
        self.counter += 1
        if self.counter % 10000 == 0:
            # Produce tree to kafka every 10 seconds
            self.client.produce(
                self.tree.build_tree(self.client.app_id))
            self.tree.clear_root()
            self._clear_for_dead_threads()

    def _clear_for_dead_threads(self):
        for thread_id in sys._current_frames().keys():
            self.sampled_times.pop(thread_id, None)

    def handle_exc(self, type, value, traceback):
        event = self.client.build_event_data(type, value, traceback,
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
