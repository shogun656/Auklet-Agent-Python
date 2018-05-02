import threading
import time
from random import randint

from auklet.monitoring import Monitoring
from auklet.example import new_func


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
        new_func()
        test_iterate()


def test_iterate():
    new_list = []
    for item in [1, 2, 3, 4, 5, 6, 7, 8]:
        if foo(item) == 2:
            new_list.append(item)
            1 / 0


def spawn_threads():
    thread_one = threading.Thread(target=random_numbers)
    thread_two = threading.Thread(target=second_thread_func)
    thread_one.start()
    thread_two.start()
    while True:
        if not thread_two.is_alive():
            thread_two = threading.Thread(target=second_thread_func)
            thread_two.start()
        else:
            time.sleep(1)


if __name__ == "__main__":
    auklet_monitoring = Monitoring("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZmY0NTNhMGItZGMwMy00YzlkLTljYTQtNzEyNzcxY2NlZTg5IiwidXNlcm5hbWUiOiI5M2UxY2U2Yi05NzIzLTRhZmUtODIxMS1iMGRkZjhiM2U0ZDgiLCJleHAiOjE1MjQxNTYzOTAsImVtYWlsIjoiIn0.TYwjasv4z9p3vXqjFFOW9upEBQiDQdVfWe_baz26tLo",
                                   "NgNFbjHsQtAepLjYqpPSaA",
                                   "https://api-staging.auklet.io/")

    auklet_monitoring.start()
    spawn_threads()
    auklet_monitoring.stop()
