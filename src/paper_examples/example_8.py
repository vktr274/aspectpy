from aspectpy.decorators import Before
from typing import Any
import re


class Aspect(type):
    before_regexp = re.compile(r"^test[1,2]$")

    def __new__(cls, name, bases, namespace):
        # Modify the class using wrappers
        print(f"Modifying the namespace: {namespace}\n")
        for attr_name, attr_value in namespace.items():
            if not callable(attr_value) or attr_name == "__init__":
                continue

            if cls.before_regexp.match(attr_name):
                namespace[attr_name] = Before(cls.action, "before", 1, 2)(attr_value)

        return super().__new__(cls, name, bases, namespace)

    @staticmethod
    def action(arg1: Any, arg2: Any, arg3: Any) -> None:
        print(f"Doing something {arg1} with args: '{arg2}' and '{arg3}'")


class MyClass(metaclass=Aspect):
    def __init__(self):
        self.example = "example"
        print("INIT: Initializing MyClass\n")

    def test1(self):
        print("TEST 1: Doing something")
        return 1

    def test2(self):
        print("TEST 2: Doing something")
        return 2

    def another_method(self):
        print("ANOTHER_METHOD: Doing something")
        return 3


my_class = MyClass()
print(f"Return value: {my_class.test1()}\n")
print(f"Return value: {my_class.test2()}\n")
print(f"Return value: {my_class.another_method()}")
