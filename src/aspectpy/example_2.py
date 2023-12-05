from typing import Any, Callable


def decorator(func: Callable[..., Any]):
    def wrapper(*args, **kwargs):
        print("Running wrapper().")
        func(*args, **kwargs)

    return wrapper


@decorator
def decorated():
    print("Running decorated().")


def explicitly_decorated():
    print("Running explicitly_decorated().")


decorated()

# This is the same as explicitly decorating
# the function like this:

decorator(explicitly_decorated)()
# or
explicitly_decorated = decorator(explicitly_decorated)
explicitly_decorated()
