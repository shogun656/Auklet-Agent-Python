from __future__ import absolute_import
import os
import itertools
from src.benchmark.statprof import statprof
from pidigits import piGenerator

__all__ = ['start']


class ThreadRing:
    def test(self, loop_counter):
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
        with open("tmp/benchmark_results", 'a') as file:
            file.write(os.path.basename(__file__) + " " + self.__class__.__name__ + " ")
        statprof.display()
        statprof.reset()


class Fibonacci:
    def test(self, loop_counter, fibonacci_range=20):
        statprof.start()
        try:
            print("\nStarting Fibonacci Sequence tests...")
            print("Running Fibonacci Sequence tests...")
            for _ in range(loop_counter):
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


def start():
    loop_counter = 10
    ThreadRing().test(loop_counter)
    Fibonacci().test(loop_counter)
    Pi().test(loop_counter)
