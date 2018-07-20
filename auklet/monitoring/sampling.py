# Portions of this file are taken from
# https://github.com/what-studio/profiling/tree/0.1.1,
# the license for which can be found in the "licenses/profiling.txt" file
# in this repository/package.
# from __future__ import absolute_import, unicode_literals
#
# import sys
# import functools
# import threading
# from auklet.base import Runnable, setup_thread_excepthook, deferral
#
#
# __all__ = ['AukletSampler']
#
#
# class AukletSampler(Runnable):
#     """Uses :func:`sys.setprofile` and :func:`threading.setprofile` to sample
#     running frames per thread.  It can be used at systems which do not support
#     profiling signals.
#     Just like :class:`profiling.tracing.timers.ThreadTimer`, `Yappi`_ is
#     required for earlier than Python 3.3.
#     .. _Yappi: https://code.google.com/p/yappi/
#     """
#     client = None
#     emission_rate = 60  # 10 seconds
#     network_rate = 10  # 10 seconds
#     hour = 3600  # 1 hour
#
#     def __init__(self, client, *args, **kwargs):
#         sys.excepthook = self.handle_exc
#         setup_thread_excepthook()
#         self.client = client
#
#     def _profile(self, queue, frame, event, arg=None):
#         queue.put(frame)
#
#     def handle_exc(self, type, value, traceback):
#         event = self.client.build_event_data(type, traceback)
#         self.client.produce(event, "event")
#         return sys.__excepthook__(type, value, traceback)
#
#     def run(self, *args, **kwargs):
#         profile = functools.partial(self._profile, kwargs['queue'])
#         with deferral() as defer:
#             sys.setprofile(profile)
#             defer(sys.setprofile)
#             threading.setprofile(profile)
#             defer(threading.setprofile)
#             yield
