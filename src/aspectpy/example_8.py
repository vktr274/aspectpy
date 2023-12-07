from decorators import Before
from typing import Any
import re


class Aspect(type):
    before_regexp = re.compile(r"^test[1,2]$")

    def __new__(cls, name, bases, namespace):
        # Modify the class using wrappers
        print(f"Modifying the namespace: {namespace}\n")
        for attr_name, attr_value in namespace.items():
            if not callable(attr_value):
                continue

            if attr_name == "__init__":
                # Explicitly calling the decorator instance
                namespace[attr_name] = Before(
                    {"example": "modified_example"}, cls.action, "before __init__", 1, 2
                )(attr_value)

            elif cls.before_regexp.match(attr_name):
                # Explicitly calling the decorator instance
                namespace[attr_name] = Before(
                    None, cls.action, f"before {attr_name}", 1, 2
                )(attr_value)

        return super().__new__(cls, name, bases, namespace)

    @staticmethod
    def action(arg1: Any, arg2: Any, arg3: Any) -> None:
        print(f"Doing something {arg1} with args: '{arg2}' and '{arg3}'")


class MyClass(metaclass=Aspect):
    def __init__(self, example):
        self.example = example
        print(f"INIT: Initializing MyClass with example = '{self.example}'")

    def test1(self):
        print("TEST 1: Doing something")
        return 1

    def test2(self):
        print("TEST 2: Doing something")
        return 2

    def another_method(self):
        print("ANOTHER_METHOD: Doing something")
        return 3


my_class = MyClass("example")
print(f"Return value: {my_class.test1()}\n")
print(f"Return value: {my_class.test2()}\n")
print(f"Return value: {my_class.another_method()}")
