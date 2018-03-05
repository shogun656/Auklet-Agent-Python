from random import randint
from auklet.profiler import SamplingProfiler


def random_numbers():
    while True:
        random_int = randint(1, 2)
        foo(random_int)


def foo(rand):
    if rand == 1:
        return bar()
    else:
        return g()


def bar():
    return []


def g():
    return 1 + 1


samplingProfiler = SamplingProfiler()

samplingProfiler.start()
random_numbers()
samplingProfiler.stop()
