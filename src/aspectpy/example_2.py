from typing import Any, Callable


def decorator(func: Callable[..., Any]):
    def wrapper(*args, **kwargs):
        print("Running wrapper().")
        func(*args, **kwargs)

    return wrapper


@decorator
def decorated():
    print("Running decorated().")


decorated()
