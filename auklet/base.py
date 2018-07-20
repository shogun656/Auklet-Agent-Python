# Portions of this file are taken from
# https://github.com/what-studio/profiling/tree/0.1.1,
# the license for which can be found in the "licenses/profiling.txt" file
# in this repository/package.
from __future__ import absolute_import, unicode_literals

import os
import sys
import uuid
import hashlib

from contextlib import contextmanager
from collections import deque
from ipify import get_ip
from ipify.exceptions import IpifyException

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError, URLError

__all__ = ['Runnable', 'frame_stack', 'deferral', 'get_commit_hash',
           'get_mac', 'get_device_ip', 'setup_thread_excepthook',
           'get_abs_path', 'u', 'b']


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
    return hashlib.md5(b(mac)).hexdigest()


def get_commit_hash():
    try:
        with open(".auklet/version", "r") as auklet_file:
            return auklet_file.read().rstrip()
    except IOError:
        # TODO Error out app if no commit hash
        return ""


def get_abs_path(path):
    try:
        return os.path.abspath(path).split('/.auklet')[0]
    except IndexError:
        return ''


def get_device_ip():
    try:
        return get_ip()
    except IpifyException:
        # TODO log to kafka if the ip service fails for any reason
        return None
    except Exception:
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
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                sys.excepthook(*sys.exc_info())

        self.run = run_with_except_hook

    threading.Thread.__init__ = init


if sys.version_info < (3,):
    # Python 2 and 3 String Compatibility
    def b(x):
        return x

    def u(x):
        return x
else:
    # https://pythonhosted.org/six/#binary-and-text-data
    import codecs

    def b(x):
        # Produces a unicode string to encoded bytes
        return codecs.utf_8_encode(x)[0]

    def u(x):
        # Produces a byte string from a unicode object
        return codecs.utf_8_decode(x)[0]


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
