from typing import Any, Callable


class DecoratorFactory:
    def __init__(self, param1: int, param2: None | str = None):
        self.param1 = param1
        self.param2 = param2

    def __call__(self, func: Callable[..., Any]):
        def wrapper(*args, **kwargs):
            print("Running wrapper().")
            print(f"Doing something with {self.param1} and {self.param2}.")
            func(*args, **kwargs)

        return wrapper


@DecoratorFactory(7)
def decorated(x: Any, y=0.1, z="string"):
    print(f"Running decorated({x}, {y}, {z}).")


decorated(["a", 0.5, 10], y=7.7, z="another string")
