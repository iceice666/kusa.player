import time


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        print(time.time() - start)
        return ret

    return wrapper
