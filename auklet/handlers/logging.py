from __future__ import absolute_import

import logging

from auklet.base import Client, get_mac


__all__ = ["AukletHandler"]


class AukletHandler(logging.Handler):
    client = None

    def __init__(self, apikey=None, app_id=None,
                 base_url="https://api.auklet.io/", *args, **kwargs):
        self.client = Client(apikey, app_id, base_url, get_mac())
        logging.Handler.__init__(self, level=kwargs.get('level', logging.NOTSET))

    def emit(self, record):
        self.format(record)
        self.client.produce(self.client.build_log_data(record), "log")
