import time
import itertools
import logging
from statprof import statprof
from pidigits import piGenerator
from mock import patch

import os, sys
parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from auklet.monitoring import Monitoring

# The tests are the same for both control_benchmark.py and auklet_benchmark.py. The comments are also alike.

class ThreadRing:
    """This test keeps 503 threads open"""
    def test(self, loop_counter):
        """
        The following descriptions are the same for all three test classes:
        - The test function is responsible for setting and running the test as well as capturing the results.
        """
        statprof.start()
        try:
            print("Starting Thread Ring tests...")
            print("Running Thread Ring tests...")
            for _ in range(loop_counter):
                self.generator()
        finally:
            statprof.stop()
            print("Thread Ring test results...")
            self.display()

    @staticmethod
    def generator(n=50000, n_threads=400, cycle=itertools.cycle):
        """
        - The generator function is responsible for a majority of the load.  This is the test.
        """
        def worker(worker_id):

            n = 1
            while True:
                if n > 0:
                    n = (yield (n - 1))
                else:
                    raise StopIteration

        thread_ring = [worker(w) for w in range(1, n_threads + 1)]
        for t in thread_ring: foo = next(t)  # start exec. gen. funcs
        send_function_ring = [t.send for t in thread_ring]  # speed...
        for send in cycle(send_function_ring):
            try:
                n = send(n)
            except StopIteration:
                break

    def display(self):
        """
        - The display function is responsible for writing the test results to a file to be used for comparing.
        -  The 'statprof' library required alteration in order to write the time to the file
            - Those changes can be found /compose/benchmark_testing/src/statprof/statprof.py:382 & 414
        """
        with open("tmp/benchmark_results", 'a') as file:
            file.write(os.path.basename(__file__) + " " + self.__class__.__name__ + " ")
        statprof.display()
        statprof.reset()


class Fibonacci:
    """This test finds the fibonacci sequence up to term 33"""
    def test(self, loop_counter, fibonacci_range=20):
        statprof.start()
        try:
            print("\nStarting Fibonacci Sequence tests...")
            print("Running Fibonacci Sequence tests...")
            for i in range(loop_counter):
                self.generator(fibonacci_range)
        finally:
            statprof.stop()
            print("Fibonacci sequence test results...")
            self.display()

    def generator(self, fibonacci_range):
        if fibonacci_range <= 1:
            return fibonacci_range
        else:
            return self.generator(fibonacci_range-1) + self.generator(fibonacci_range-2)

    def display(self):
        with open("tmp/benchmark_results", 'a') as file:
            file.write(os.path.basename(__file__) + " " + self.__class__.__name__ + " ")
        statprof.display()
        statprof.reset()


class Pi:
    """This test finds the first 10,000 digits of pi"""
    def test(self, loop_counter, number_of_pi_digits=1000):
        statprof.start()
        try:
            print("\nStarting Pi Generator tests...")
            print("Running Pi Generator tests...")
            for _ in range(loop_counter):
                self.generator(number_of_pi_digits)
        finally:
            statprof.stop()
            print("Pi Generator test results...")
            self.display()

    @staticmethod
    def generator(number_of_digits):
        my_pi = piGenerator()
        return [next(my_pi) for _ in range(number_of_digits)]

    def display(self):
        with open("tmp/benchmark_results", 'a') as file:
            file.write(os.path.basename(__file__) + " " + self.__class__.__name__ + " ")
        statprof.display()
        statprof.reset()


def run_tests():
    print("\n\nStarting benchmark tests with the Auklet Agent...")
    loop_counter = 10

    ThreadRing().test(loop_counter)
    Fibonacci().test(loop_counter)
    Pi().test(loop_counter)


@patch('auklet.base.Client.update_limits')
@patch('auklet.base.Client._get_kafka_certs')
def auklet_benchmark_main(get_kafka_certs_mock, update_limits_mock):
    def _get_kafka_brokers(self):
        self.brokers = ["kafka:9093"]
        self.producer_types = {
            "monitoring": "profiling",
            "event": "events",
            "log": "logging"
        }
    update_limits_mock.return_value = 10000
    get_kafka_certs_mock.return_value = True

    patcher = patch('auklet.base.Client._get_kafka_brokers', new=_get_kafka_brokers)
    patcher.start()
    auklet_monitoring = Monitoring("", "", monitoring=True)
    auklet_monitoring.start()
    run_tests()
    auklet_monitoring.stop()
    patcher.stop()