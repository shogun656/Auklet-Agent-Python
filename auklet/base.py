from __future__ import absolute_import

import os
import io
import sys
import uuid
import json
import errno
import zipfile
import requests

from uuid import uuid4
from datetime import datetime
from contextlib import contextmanager
from collections import deque
from kafka import KafkaProducer
from kafka.errors import KafkaError
from auklet.stats import Event, SystemMetrics
from ipify import get_ip

__all__ = ['Client', 'Runnable', 'frame_stack', 'deferral', 'thread_clock',
           'get_mac', 'setup_thread_excepthook']


class Client(object):
    producer_types = {
        "profiler_data": "staging-profiler",
        "event": "staging-events"
    }

    def __init__(self, apikey=None, app_id=None):
        self.apikey = os.environ.get('AUKLET_API_KEY', apikey)
        self.app_id = os.environ.get('AUKLET_APP_ID', app_id)
        self.base_url = "https://api-staging.auklet.io/"
        self.send_enabled = True
        self.producer = None
        if self._get_kafka_certs():
            try:
                self.producer = KafkaProducer(**{
                    "bootstrap_servers": "kafka-staging.auklet.io:9093",
                    "ssl_cafile": "tmp/ck_ca.pem",
                    "ssl_certfile": "tmp/ck_cert.pem",
                    "ssl_keyfile": "tmp/ck_private_key.pem",
                    "security_protocol": "SSL",
                    "ssl_check_hostname": False,
                    "value_serializer": lambda m: json.dumps(m)
                })
            except KafkaError:
                pass
        self.profiler_topic = "staging-profiler"
        self.event_topic = "staging-events"

    def _build_url(self, extension):
        return '%s%s' % (self.base_url, extension)

    def _create_kafka_cert_location(self, filename):
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        return True

    def _get_kafka_certs(self):
        res = requests.get(self._build_url("private/devices/certificates/"),
                           headers={"Authorization": "JWT %s" % self.apikey})
        mlz = zipfile.ZipFile(io.BytesIO(res.content))
        for temp_file in mlz.filelist:
            filename = "tmp/%s.pem" % temp_file.filename
            self._create_kafka_cert_location(filename)
            f = open(filename, "wb")
            f.write(mlz.open(temp_file.filename).read())
        return True

    def build_event_data(self, type, value, traceback, tree):
        event = Event(type, value, traceback, tree)
        event_dict = dict(event)
        event_dict['application'] = self.app_id
        event_dict['publicIP'] = get_ip()
        event_dict['id'] = str(uuid4())
        event_dict['timestamp'] = datetime.now()
        event_dict['system_metrics'] = dict(SystemMetrics())
        event_dict['mac_address_hash'] = get_mac()
        return event_dict

    def produce(self, data, data_type="profiler"):
        if self.producer is not None:
            self.producer.send(self.producer_types[data_type], value=data)


# Requires Rewriting
# Everything below this line is a candidate for rewriting
class Runnable(object):
    """The base class for runnable classes such as :class:`profiling.profiler.
    Profiler`.
    """

    #: The generator :meth:`run` returns.  It will be set by :meth:`start`.
    _running = None

    def is_running(self):
        """Whether the instance is running."""
        return self._running is not None

    def start(self, *args, **kwargs):
        """Starts the instance.
        :raises RuntimeError: has been already started.
        :raises TypeError: :meth:`run` is not canonical.
        """
        if self.is_running():
            raise RuntimeError('Already started')
        self._running = self.run(*args, **kwargs)
        try:
            yielded = next(self._running)
        except StopIteration:
            raise TypeError('run() must yield just one time')
        if yielded is not None:
            raise TypeError('run() must yield without value')

    def stop(self):
        """Stops the instance.
        :raises RuntimeError: has not been started.
        :raises TypeError: :meth:`run` is not canonical.
        """
        if not self.is_running():
            raise RuntimeError('Not started')
        running, self._running = self._running, None
        try:
            next(running)
        except StopIteration:
            # expected.
            pass
        else:
            raise TypeError('run() must yield just one time')

    def run(self, *args, **kwargs):
        """Override it to implement the starting and stopping behavior.
        An overriding method must be a generator function which yields just one
        time without any value.  :meth:`start` creates and iterates once the
        generator it returns.  Then :meth:`stop` will iterates again.
        :raises NotImplementedError: :meth:`run` is not overridden.
        """
        raise NotImplementedError('Implement run()')
        yield

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_info):
        self.stop()


def frame_stack(frame, base_frame=None, base_code=None,
                ignored_frames=(), ignored_codes=()):
    """Returns a deque of frame stack."""
    frames = deque()
    while frame is not None:
        if frame is base_frame or frame.f_code is base_code:
            break
        if frame in ignored_frames or frame.f_code in ignored_codes:
            pass
        else:
            frames.appendleft(frame)
        frame = frame.f_back
    return frames


def get_mac():
    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
    mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
    return mac


def setup_thread_excepthook():
    import threading
    """
    Workaround for `sys.excepthook` thread bug from:
    http://bugs.python.org/issue1230540

    Call once from the main thread before creating any threads.
    """
    init_original = threading.Thread.__init__

    def init(self, *args, **kwargs):

        init_original(self, *args, **kwargs)
        run_original = self.run

        def run_with_except_hook(*args2, **kwargs2):
            try:
                run_original(*args2, **kwargs2)
            except Exception:
                sys.excepthook(*sys.exc_info())

        self.run = run_with_except_hook

    threading.Thread.__init__ = init


@contextmanager
def deferral():
    """Defers a function call when it is being required like Go.
    ::
       with deferral() as defer:
           sys.setprofile(f)
           defer(sys.setprofile, None)
           # do something.
    """
    deferred = []
    defer = lambda func, *args, **kwargs: deferred.append(
        (func, args, kwargs))
    try:
        yield defer
    finally:
        while deferred:
            func, args, kwargs = deferred.pop()
            func(*args, **kwargs)


if sys.version_info < (3, 3):
    def thread_clock():
        import yappi
        return yappi.get_clock_time()
else:
    import time
    def thread_clock():
        return time.clock_gettime(time.CLOCK_THREAD_CPUTIME_ID)
