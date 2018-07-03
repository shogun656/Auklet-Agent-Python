import sys
import unittest

os.chdir("../..")
from auklet.monitoring import MonitoringBase, Monitoring

#
# class TestMonitoringBase(unittest.TestCase):
#     def setUp(self):
#         self.function = MonitoringBase()
#
#     def testStart(self):
#         print(self.function.start())


class TestMonitoring(unittest.TestCase):
    def setUp(self):
        self.function = Monitoring(
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiODE2YjlkOTItYjg0Yi00OGUzLWI1ZDQtYmYwMGZiODBhOTU3IiwidXNlcm5hbWUiOiIyMjBhYzVlMy1iZGEyLTRmYmQtYTJiZi1lZDYyNWRjMGM0N2EiLCJleHAiOjE1Mjk1OTI3ODksImVtYWlsIjoiIn0.6eWsEoAnVMHkAf4Vy2-WOjxicB5KKrKBHzTFG63ZI3g",
            "jWmc4aPf5XnHHjiNbLyyNB",
            base_url="https://api-staging.auklet.io/",
            monitoring=True)

    def testStart(self):
        self.assertTrue(self.function.monitor)
        self.function.monitor = False
        self.assertFalse(self.function.monitor)

    def testSample(self):
        frame = None
        event = "call"
        self.assertFalse(self.function.sample(frame, event).increment_call)


if __name__ == "__main__":
    unittest.main()
