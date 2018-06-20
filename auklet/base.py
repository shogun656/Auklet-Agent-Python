# Portions of this file are taken from
# https://github.com/what-studio/profiling/tree/0.1.1,
# the license for which can be found in the "licenses/profiling.txt" file
# in this repository/package.
from __future__ import absolute_import, unicode_literals

import json

from uuid import uuid4
from datetime import datetime
from kafka.errors import KafkaError
from auklet import utils
from auklet.utils import u
from auklet.stats import Event, SystemMetrics

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError, URLError

__all__ = ['Client', 'Runnable']

MB_TO_B = 1e6
S_TO_MS = 1000


class Client(object):
    producer_types = None
    brokers = None
    commit_hash = None
    mac_hash = None
    offline_filename = ".auklet/local.txt"
    limits_filename = ".auklet/limits"
    usage_filename = ".auklet/usage"
    com_config_filename = ".auklet/communication"
    abs_path = None

    reset_data = False
    data_day = 1
    data_limit = None
    data_current = 0
    offline_limit = None
    offline_current = 0

    system_metrics = None

    def __init__(self, apikey=None, app_id=None,
                 base_url="https://api.auklet.io/", mac_hash=None):
        self.apikey = apikey
        self.app_id = app_id
        self.base_url = base_url
        self.send_enabled = True
        self.producer = None
        self.mac_hash = mac_hash
        self._load_limits()
        utils.create_file(self.offline_filename)
        utils.create_file(self.limits_filename)
        utils.create_file(self.usage_filename)
        utils.create_file(self.com_config_filename)
        self.commit_hash = utils.get_commit_hash()
        self.abs_path = utils.get_abs_path(".auklet/version")
        self.system_metrics = SystemMetrics()

    def _get_config(self):
        res = utils.open_auklet_url(
            utils.build_url(
                "private/devices/{}/app_config/".format(self.app_id)))
        if res is not None:
            return json.loads(u(res.read()))['config']

    def _load_limits(self):
        try:
            with open(self.limits_filename, "r") as limits:
                limits_str = limits.read()
                if limits_str:
                    data = json.loads(limits_str)
                    self.data_day = data['data']['normalized_cell_plan_date']
                    temp_limit = data['data']['cellular_data_limit']
                    if temp_limit is not None:
                        self.data_limit = data['data'][
                                              'cellular_data_limit'] * MB_TO_B
                    else:
                        self.data_limit = temp_limit
                    temp_offline = data['storage']['storage_limit']
                    if temp_offline is not None:
                        self.offline_limit = data['storage'][
                                                 'storage_limit'] * MB_TO_B
                    else:
                        self.offline_limit = data['storage']['storage_limit']
        except IOError:
            return

    def _build_usage_json(self):
        return {"data": self.data_current, "offline": self.offline_current}

    def _update_usage_file(self):
        try:
            with open(self.usage_filename, 'w') as usage:
                usage.write(json.dumps(self._build_usage_json()))
        except IOError:
            return False

    def _check_data_limit(self, data, current_use, offline=False):
        if self.offline_limit is None and offline:
            return True
        if self.data_limit is None and not offline:
            return True
        data_size = len(json.dumps(data))
        temp_current = current_use + data_size
        if temp_current >= self.data_limit:
            return False
        if offline:
            self.offline_current = temp_current
        else:
            self.data_current = temp_current
        self._update_usage_file()
        return True

    def update_network_metrics(self, interval):
        self.system_metrics.update_network(interval)

    def check_date(self):
        if datetime.today().day == self.data_day:
            if self.reset_data:
                self.data_current = 0
                self.reset_data = False
        else:
            self.reset_data = True

    def update_limits(self):
        config = self._get_config()
        if config is None:
            return 60
        with open(self.limits_filename, 'w+') as limits:
            limits.truncate()
            limits.write(json.dumps(config))
        new_day = config['data']['normalized_cell_plan_date']
        temp_limit = config['data']['cellular_data_limit']
        if temp_limit is not None:
            new_data = config['data']['cellular_data_limit'] * MB_TO_B
        else:
            new_data = temp_limit
        temp_offline = config['storage']['storage_limit']
        if temp_offline is not None:
            new_offline = config['storage']['storage_limit'] * MB_TO_B
        else:
            new_offline = config['storage']['storage_limit']
        if self.data_day != new_day:
            self.data_day = new_day
            self.data_current = 0
        if self.data_limit != new_data:
            self.data_limit = new_data
        if self.offline_limit != new_offline:
            self.offline_limit = new_offline
        # return emission period in ms
        return config['emission_period'] * S_TO_MS

    def build_event_data(self, type, traceback, tree):
        event = Event(type, traceback, tree, self.abs_path)
        event_dict = dict(event)
        event_dict['application'] = self.app_id
        event_dict['publicIP'] = utils.get_device_ip()
        event_dict['id'] = str(uuid4())
        event_dict['timestamp'] = str(datetime.utcnow())
        event_dict['systemMetrics'] = dict(self.system_metrics)
        event_dict['macAddressHash'] = self.mac_hash
        event_dict['commitHash'] = self.commit_hash
        return event_dict

    def build_log_data(self, msg, data_type, level):
        log_dict = {
            "message": msg,
            "type": data_type,
            "level": level,
            "application": self.app_id,
            "publicIP": utils.get_device_ip(),
            "id": str(uuid4()),
            "timestamp": str(datetime.utcnow()),
            "systemMetrics": dict(SystemMetrics()),
            "macAddressHash": self.mac_hash,
            "commitHash": self.commit_hash
        }
        return log_dict


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
