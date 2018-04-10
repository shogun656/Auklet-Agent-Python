import threading
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


def second_thread_func():
    while True:
        test_iterate()


def test_iterate():
    new_list = []
    for item in [1, 2, 3, 4, 5, 6, 7, 8]:
        if foo(item) == 2:
            new_list.append(item)


def spawn_threads():
    thread_one = threading.Thread(target=random_numbers)
    thread_two = threading.Thread(target=second_thread_func)
    thread_one.start()
    thread_two.start()


samplingProfiler = SamplingProfiler("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiNWFhMjM4YzctZGUwYy00ODdlLWFjZmItZThmMzE1Y2VmNGUyIiwidXNlcm5hbWUiOiJmOWY1MThmOS01YTFlLTQ4MDQtOTJkOS1mNzFjZDkyNmQyZGQiLCJleHAiOjE1MjA2MjMwMjgsImVtYWlsIjoiIn0.fLvlFlsB3X5aF8ft0pKl97qgcj-LYfFuw9cE4MGG_U0",
                                    "aVEmhNVG4otKYDbwwJRaSi",
                                    "https://api-staging.auklet.io/")

samplingProfiler.start()
spawn_threads()
samplingProfiler.stop()
