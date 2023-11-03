from aspectpy.decorators import Before, AfterReturning, AfterThrowing, Around
from inspect import get_annotations, getargs
import re


class Aspect(type):
    before_regexp = re.compile(r"^test[1-3]$")
    after_returning_regexp = re.compile(r"^test[4-6]$")
    after_throwing_regexp = re.compile(r"^test[5-7]$")
    around_regexp = re.compile(r"^test[_]?8$")

    def __new__(cls, name, bases, attrs):
        # Modify the class using wrappers
        for attr_name, attr_value in attrs.items():
            stored_value = attr_value
            if not callable(attr_value) or attr_name == "__init__":
                continue

            if cls.before_regexp.match(attr_name):
                attrs[attr_name] = Before(cls.action, "before", 1, 2)(stored_value)
                stored_value = attrs[attr_name]

            if cls.after_returning_regexp.match(attr_name):
                attrs[attr_name] = AfterReturning(cls.action, "after returning", 2, 3)(
                    stored_value
                )
                stored_value = attrs[attr_name]

            if cls.after_throwing_regexp.match(attr_name):
                attrs[attr_name] = AfterThrowing(cls.action, "after throwing", 3, 4)(
                    stored_value
                )
                stored_value = attrs[attr_name]

            if cls.around_regexp.match(attr_name):
                attrs[attr_name] = Around(
                    cls.proceed,
                    cls.action,
                    "around",
                    4,
                    5,
                )(stored_value)
                stored_value = attrs[attr_name]
        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def action(arg1, arg2, arg3):
        print(f"Doing something {arg1} with args: '{arg2}' and '{arg3}'")
        return 0.1

    @staticmethod
    def proceed(func):
        args = getargs(func.__code__).args
        return_type = get_annotations(func).get("return", None)
        print(
            f"Evaluating whether to proceeed with args: {args} and return type: {return_type}"
        )
        return return_type == str and "number" in args
