import os
import sys
import uuid
import hashlib

from contextlib import contextmanager
from collections import deque
from ipify import get_ip
from ipify.exceptions import IpifyException
from auklet.errors import AukletConfigurationError

__all__ = ['open_auklet_url', 'create_file', 'clear_file', 'build_url',
           'frame_stack', 'deferral', 'get_commit_hash', 'get_mac',
           'get_device_ip', 'setup_thread_excepthook', 'get_abs_path', 'b', 'u']

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError, URLError


def open_auklet_url(self, url):
    url = Request(url, headers={"Authorization": "JWT %s" % self.apikey})
    try:
        res = urlopen(url)
    except HTTPError as e:
        if e.code == 401:
            raise AukletConfigurationError(
                "Invalid configuration of Auklet Monitoring, "
                "ensure proper API key and app ID passed to "
                "Monitoring class"
            )
        raise e
    except URLError:
        return None
    return res


def create_file(self, filename):
    open(filename, "a").close()


def clear_file(self, file_name):
    open(file_name, "w").close()


def build_url(self, extension):
    return '%s%s' % (self.base_url, extension)


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
        sys.exit("No Commit Hash found")


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
            except Exception:
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
