from __future__ import absolute_import
import random
import string
from src.benchmark.statprof import statprof
from pidigits import piGenerator

__all__ = ['start']


class Fibonacci:
    def test(self, fibonacci_range=28):
        if fibonacci_range <= 1:
            return fibonacci_range
        else:
            return self.test(fibonacci_range-1) + self.test(fibonacci_range-2)


class PiDigits:
    @staticmethod
    def test(number_of_digits=30000):
        my_pi = piGenerator()
        return [next(my_pi) for _ in range(number_of_digits)]


class Addition:
    @staticmethod
    def test(number_of_iterations=10000000):
        total = 0
        for i in range(1, number_of_iterations):
            total = total + i


class Multiplication:
    @staticmethod
    def test(number_of_iterations=80000):
        total = 1
        for i in range(1, number_of_iterations):
            total = total * i


class Division:
    @staticmethod
    def test(number_of_iterations=1000000):
        total = 1
        for i in range(1, number_of_iterations):
            total = total / i


class WriteToDisk:
    @staticmethod
    def test():
        with open("/tmp/write-read", "w") as file:
            file.write(''.join(random.SystemRandom().choice(
                string.ascii_letters + string.digits) for _ in range(50000)))


class ReadFromDisk:
    @staticmethod
    def test():
        with open("/tmp/write-read", "r") as file:
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
    with open("/tmp/benchmark_results", "a") as file:
        file.write(state + " " + test_name + " ")
    statprof.display()
    statprof.reset()


def start(state):
    tests = [Fibonacci, PiDigits, Addition,
             Multiplication, Division, WriteToDisk, ReadFromDisk]

    for test in tests:
        runtest(state, test())

