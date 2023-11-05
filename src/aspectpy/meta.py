from typing import Any, Callable
from aspectpy.decorators import Before, AfterReturning, AfterThrowing, Around
from inspect import get_annotations, getargs
import re


class Aspect(type):
    before_regexp = re.compile(r"^test[1-3]$")
    after_returning_regexp = re.compile(r"^test[4-6]$")
    around_regexp = re.compile(r"^test[_]?7$")
    after_throwing_regexp = re.compile(r"^test[8,9]$")

    def __new__(cls, name, bases, namespace):
        # Modify the class using wrappers
        for attr_name, attr_value in namespace.items():
            stored_value = attr_value
            if not callable(attr_value) or attr_name == "__init__":
                continue

            if cls.before_regexp.match(attr_name):
                namespace[attr_name] = Before(cls.action, "before", 1, 2)(stored_value)
                stored_value = namespace[attr_name]

            if cls.after_returning_regexp.match(attr_name):
                namespace[attr_name] = AfterReturning(
                    cls.action, "after returning", 2, 3
                )(stored_value)
                stored_value = namespace[attr_name]

            if cls.after_throwing_regexp.match(attr_name):
                namespace[attr_name] = AfterThrowing(
                    ValueError, cls.action, "after throwing", 3, 4
                )(stored_value)
                stored_value = namespace[attr_name]

            if cls.around_regexp.match(attr_name):
                namespace[attr_name] = Around(
                    cls.proceed,
                    cls.action,
                    "around",
                    4,
                    5,
                )(stored_value)
                stored_value = namespace[attr_name]
        return super().__new__(cls, name, bases, namespace)

    @staticmethod
    def action(arg1: Any, arg2: Any, arg3: Any) -> float:
        print(f"Doing something {arg1} with args: '{arg2}' and '{arg3}'")
        return 0.1

    @staticmethod
    def proceed(func: Callable[..., Any]) -> bool:
        args = getargs(func.__code__).args
        return_type = get_annotations(func).get("return", None)
        print(
            f"Evaluating whether to proceeed with args: {args} and return type: {return_type}"
        )
        return return_type == str and "number" in args
