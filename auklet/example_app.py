from random import randint
from auklet.profiler import SamplingProfiler
#from auklet.base import Client


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


# client = Client('7420da40386d17ea8bc6aafbf50b03e1fef65c704f9d296cd8e1b32352790728c8f12abbd3ddff2340a5eac3dabb463c1849d29ff2f3c85279828c9e396e5d64', '5a0ba207-4078-4bf1-8cce-559e3370a9bc')
# client.produce()


samplingProfiler = SamplingProfiler()

samplingProfiler.start()
random_numbers()
samplingProfiler.stop()
