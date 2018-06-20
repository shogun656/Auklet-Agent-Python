from __future__ import absolute_import
import random
import string
import itertools
from src.benchmark.statprof import statprof
from pidigits import piGenerator

__all__ = ['start']


class ThreadRing:
    @staticmethod
    def worker():
        n = 1
        while True:
            if n > 0:
                n = (yield(n - 1))
            else:
                raise StopIteration

    def test(self, n=500000, n_threads=400, cycle=itertools.cycle):
        thread_ring = [self.worker() for _ in range(1, n_threads + 1)]
        for t in thread_ring:
            next(t)  # start exec. gen. funcs
        send_function_ring = [t.send for t in thread_ring]  # speed...
        for send in cycle(send_function_ring):
            try:
                n = send(n)
            except StopIteration:
                break


class Fibonacci:
    def test(self, fibonacci_range=25):
        if fibonacci_range <= 1:
            return fibonacci_range
        else:
            return self.test(fibonacci_range-1) + self.test(fibonacci_range-2)


class PiDigits:
    @staticmethod
    def test(number_of_digits=10000):
        my_pi = piGenerator()
        return [next(my_pi) for _ in range(number_of_digits)]


class Addition:
    @staticmethod
    def test(number_of_iterations=1000000):
        total = 0
        for i in range(1, number_of_iterations):
            total = total + i


class Multiplication:
    @staticmethod
    def test(number_of_iterations=50000):
        total = 1
        for i in range(1, number_of_iterations):
            total = total * i


class Division:
    @staticmethod
    def test(number_of_iterations=50000):
        total = 1
        for i in range(1, number_of_iterations):
            total = total / i


class WriteToDisk:
    @staticmethod
    def test():
        with open("tmp/write-read", "w") as file:
            file.write(''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50000)))


class ReadFromDisk:
    @staticmethod
    def test():
        with open("tmp/write-read", "r") as file:
            _ = file.read()


def runtest(state, object):
    statprof.start()
    test_name = object.__class__.__name__
    try:
        print("\nStarting %s tests..." % test_name)
        print("Running %s tests..." % test_name)
        object.test()
    finally:
        statprof.stop()
        print("%s test results..." % test_name)
        display(state, test_name)


def display(state, test_name):
    with open("tmp/benchmark_results", "a") as file:
        file.write(state + " " + test_name + " ")
    statprof.display()
    statprof.reset()


def start(state):
    tests = [ThreadRing, Fibonacci, PiDigits, Addition, Multiplication, Division, WriteToDisk, ReadFromDisk]

    for test in tests:
        runtest(state, test())

