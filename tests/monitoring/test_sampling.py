import os
import unittest

os.chdir("../..")
from auklet.monitoring.sampling import AukletSampler

class TestAukletSampler(unittest.TestCase):
    def setUp(self):
        self.auklet_sampler = AukletSampler(client=None, tree="tree")

    def test_profile(self):
        pass

    def test_handle_exc(self):
        pass

    def test_run(self):
        pass