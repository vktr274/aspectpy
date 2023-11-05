from typing import Any, Callable


def decorator_factory(param1: int, param2: None | str = None):
    def decorator(func: Callable[..., Any]):
        def wrapper(*args, **kwargs):
            print("Running wrapper().")
            print(f"Doing something with {param1} and {param2}.")
            func(*args, **kwargs)

        return wrapper

    return decorator


@decorator_factory(7)
def decorated(x: Any, y=0.1, z="string"):
    print(f"Running decorated({x}, {y}, {z}).")


decorated(("X", "Y"), y=0.7)
