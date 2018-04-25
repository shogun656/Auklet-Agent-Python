from __future__ import absolute_import

import os
import io
import sys
import uuid
import json
import errno
import zipfile
import hashlib

from uuid import uuid4
from datetime import datetime
from contextlib import contextmanager
from collections import deque
from kafka import KafkaProducer
from kafka.errors import KafkaError
from auklet.stats import Event, SystemMetrics
from ipify import get_ip
from ipify.exceptions import IpifyException

try:
    # For Python 3.0 and later
    from urllib import urlopen
    from urllib.error import HTTPError
    from urllib.request import Request
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError

__all__ = ['Client', 'Runnable', 'frame_stack', 'deferral', 'get_commit_hash',
           'get_mac', 'get_device_ip', 'setup_thread_excepthook']


class Client(object):
    producer_types = None
    brokers = None
    commit_hash = None
    mac_hash = None

    def __init__(self, apikey=None, app_id=None,
                 base_url="https://api.auklet.io/", mac_hash=None):
        self.apikey = apikey
        self.app_id = app_id
        self.base_url = base_url
        self.send_enabled = True
        self.producer = None
        self._get_kafka_brokers()
        self.mac_hash = mac_hash
        self.commit_hash = get_commit_hash()
        if self._get_kafka_certs():
            try:
                self.producer = KafkaProducer(**{
                    "bootstrap_servers": self.brokers,
                    "ssl_cafile": "tmp/ck_ca.pem",
                    "ssl_certfile": "tmp/ck_cert.pem",
                    "ssl_keyfile": "tmp/ck_private_key.pem",
                    "security_protocol": "SSL",
                    "ssl_check_hostname": False,
                    "value_serializer": lambda m: json.dumps(m)
                })
            except KafkaError:
                # TODO log off to kafka if kafka fails to connect
                pass

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

    def _get_kafka_brokers(self):
        url = Request(self._build_url("private/devices/config/"),
                      headers={"Authorization": "JWT %s" % self.apikey})
        res = urlopen(url)
        kafka_info = json.loads(res.read())
        self.brokers = kafka_info['brokers']
        self.producer_types = {
            "monitoring": kafka_info['prof_topic'],
            "event": kafka_info['event_topic'],
            "log": kafka_info['log_topic']
        }

    def _get_kafka_certs(self):
        url = Request(self._build_url("private/devices/certificates/"),
                      headers={"Authorization": "JWT %s" % self.apikey})
        try:
            res = urlopen(url)
        except HTTPError as e:
            # Allow for accessing redirect w/o including the
            # Authorization token.
            res = urlopen(e.geturl())
        mlz = zipfile.ZipFile(io.BytesIO(res.read()))
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
        event_dict['publicIP'] = get_device_ip()
        event_dict['id'] = str(uuid4())
        event_dict['timestamp'] = datetime.now().isoformat()
        event_dict['systemMetrics'] = dict(SystemMetrics())
        event_dict['macAddressHash'] = self.mac_hash
        event_dict['commitHash'] = self.commit_hash
        return event_dict

    def produce(self, data, data_type="monitoring"):
        print data
        if self.producer is not None:
            try:
                self.producer.send(self.producer_types[data_type], value=data)
            except KafkaError:
                # For now just drop the data, will want to write to a local
                # file in the future
                pass


class Runnable(object):
    """The base class for runnable classes such as :class:`monitoring.
    MonitoringBase`.
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


def frame_stack(frame):
    """Returns a deque of frame stack."""
    frames = deque()
    while frame is not None:
        frames.appendleft(frame)
        frame = frame.f_back
    return frames


def get_mac():
    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
    mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
    return hashlib.md5(mac).hexdigest()


def get_commit_hash():
    try:
        with open(".auklet/version", "r") as auklet_file:
            return auklet_file.read()
    except IOError:
        # TODO Error out app if no commit hash
        return ""


def get_device_ip():
    try:
        return get_ip()
    except IpifyException:
        # TODO log to kafka if the ip service fails for any reason
        return None


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
    """Defers a function call when it is being required.
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
