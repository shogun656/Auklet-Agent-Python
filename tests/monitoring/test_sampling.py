import unittest
from mock import patch

from auklet.monitoring.sampling import AukletSampler
from auklet.monitoring import Monitoring
from auklet.stats import MonitoringTree
from auklet.base import Client
from auklet.broker import KafkaClient


class TestAukletSampler(unittest.TestCase):
    def setUp(self):
        def _load_conf(self):
            self.brokers = ["api-staging.auklet.io:9093"]
            self.producer_types = {
                "monitoring": "profiling",
                "event": "events",
                "log": "logging"
            }

        def update_limits(self):
            pass

        def _get_certs(self):
            return True

        self.patcher = patch(
            'auklet.broker.Profiler._load_conf', new=_load_conf)
        self.patcher2 = patch(
            'auklet.base.Client.update_limits', new=update_limits)
        self.patcher3 = patch(
            'auklet.broker.KafkaClient._get_certs', new=_get_certs)
        self.patcher.start()
        self.patcher3.start()
        self.patcher2.start()

        self.monitoring = Monitoring(
            apikey="", app_id="",
            base_url="https://api-staging.auklet.io/", kafka=True)
        self.client = Client(
            apikey="", app_id="", base_url="https://api-staging.auklet.io/")
        self.broker = KafkaClient(self.client)

        self.monitoring_tree = MonitoringTree()
        self.monitoring_tree.root_func = \
            {"key": self.monitoring_tree.get_filename}
        self.tree = self.monitoring_tree
        self.auklet_sampler = AukletSampler(
            client=self.client, broker=self.broker, tree=self.tree)

    def test_profile(self):
        pass
        # class CoCode:
        #     co_code = None
        #     co_firstlineno = None
        #     co_name = None
        #
        # class Frame:
        #     f_back = None
        #     f_code = CoCode()
        #
        # def produce(self, event):
        #     global test_profile_event  # used to test if events produced
        #     test_profile_event = event
        #
        # with patch('auklet.base.Client.produce', new=produce):
        #     self.auklet_sampler.prev_diff = 1
        #     self.auklet_sampler._profile(
        #         profiler=self.monitoring, frame=Frame(), event="", arg="")
        #     # self.assertNotEqual(test_profile_event, None) # global used here

    def test_handle_exc(self):
        def build_event_data(self, type="", value="", traceback=""):
            return {"commitHash": "", "id": "", "tree":
                    {"lineNumber": 1,
                     "nSamples": 173756,
                     "functionName": "root",
                     "nCalls": 1,
                     "callees": []},
                    "publicIP": "0.0.0.0",
                    "timestamp": 1530555317012,
                    "application": "tyJSjp3aSyxxdoGAtqsMT4",
                    "macAddressHash": ""}

        def produce(self, event, topic):
            global test_handle_exc_event  # used to test if events produced
            test_handle_exc_event = event
            _ = topic

        with patch('auklet.base.Client.build_event_data',
                   new=build_event_data):
            with patch('auklet.broker.KafkaClient.produce', new=produce):
                self.auklet_sampler.handle_exc(
                    type=None, value="", traceback="")
                self.assertIsNotNone(test_handle_exc_event)  # global used here

    def test_run(self):
        self.assertNotEqual(self.auklet_sampler.run(profiler=""), None)


if __name__ == '__main__':
    unittest.main()