from typing import Any, Callable
from aspectpy.decorators import (
    Before,
    AfterReturning,
    AfterThrowing,
    Around,
    after_returning_arg_check,
)
from inspect import signature
import re


class Aspect(type):
    before_regexp = re.compile(r"^test[1-3]$")
    after_returning_regexp = re.compile(r"^test[4-6]$")
    around_regexp = re.compile(r"^test[_]?7$")
    after_throwing_regexp = re.compile(r"^test([8,9]|10)$")

    def __new__(cls, name, bases, namespace):
        # Modify the class using wrappers
        for attr_name, attr_value in namespace.items():
            stored_value = attr_value
            if not callable(attr_value) or attr_name == "__init__":
                continue

            if cls.before_regexp.match(attr_name):
                namespace[attr_name] = Before(None, None, cls.action, "before", 1, 2)(
                    stored_value
                )
                stored_value = namespace[attr_name]

            if cls.after_returning_regexp.match(attr_name):
                namespace[attr_name] = AfterReturning(
                    None, None, cls.action_after_returning, "after returning", 2, 3
                )(stored_value)
                stored_value = namespace[attr_name]

            if cls.after_throwing_regexp.match(attr_name):
                namespace[attr_name] = AfterThrowing(
                    None,
                    None,
                    (ConnectionError, ValueError),
                    cls.action,
                    "after throwing",
                    3,
                    4,
                )(stored_value)
                stored_value = namespace[attr_name]

            if cls.around_regexp.match(attr_name):
                namespace[attr_name] = Around(
                    None,
                    None,
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
        print(f"ACTION: Doing something {arg1} with args: '{arg2}' and '{arg3}'")
        return 0.1

    @staticmethod
    @after_returning_arg_check
    def action_after_returning(
        _RETURNED_VAL_: Any, arg1: Any, arg2: Any, arg3: Any
    ) -> Any:
        print(f"ACTION: Doing something {arg1} with args: '{arg2}' and '{arg3}'")
        print(f"ACTION: Doubling the returned value: {_RETURNED_VAL_}")
        return _RETURNED_VAL_ * 2

    @staticmethod
    def proceed(func: Callable[..., Any]) -> bool:
        sig = signature(func)
        params = sig.parameters.keys()
        return_type = sig.return_annotation
        print(
            f"PROCEED: Evaluating whether to proceeed with params: {params} and return type: {return_type}"
        )
        return return_type == str and "number" in params
