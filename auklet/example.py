__all__ = ['new_func']


def new_func():
    from auklet.example_app import g
    for item1 in [1, 2, 3, 4, 5, 6, 7, 8]:
        for item2 in [1, 2, 3, 4, 5, 6, 7, 8]:
            g()
    return
