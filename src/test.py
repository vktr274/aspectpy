from typing import Any
from aspectpy.decorators import (
    Before,
    AfterReturning,
    AfterThrowing,
    Around,
    validate_after_returning_action,
)
from aspectpy.meta import Aspect


@validate_after_returning_action
def action_after_returning(_RETURNED_VAL_: Any, num: int, text: str | None = None):
    print(f"ACTION {num}: with text {text} and return value {_RETURNED_VAL_}")
    return _RETURNED_VAL_ * 2


def action(num: int, text: str | None = None):
    print(f"ACTION {num}: with text {text}")


@Before(None, action, 1, text="before")
def test_before(test_text: str):
    """
    This docstring will be returned by test_before.__doc__
    because of @wraps(func) used in decorators.py
    """
    print(f"TEST_BEFORE: Doing something {test_text} 1")
    return test_text


@AfterReturning(None, action_after_returning, 2, text="after returning")
def test_after_returning(test_text: str):
    """
    This docstring will be returned by test_after_returning.__doc__
    because of @wraps(func) used in decorators.py
    """
    print(f"TEST_AFTER_RETURNING: Doing something {test_text} 2")
    return test_text


@AfterThrowing(
    {"test_text": "SUSPICIOUS and MODIFIED", "num": 3},
    None,
    action,
    3,
    "after throwing",
)
def test_after_throwing(test_text: str, throw: bool = False, num: int = 0):
    """
    This docstring will be returned by test_after_throwing.__doc__
    because of @wraps(func) used in decorators.py
    """
    print(
        f"TEST_AFTER_THROWING: Doing something {test_text} with {num} that might throw an exception"
    )
    if throw:
        raise Exception("Exception thrown")
    return test_text


def proceed(func) -> bool:
    print(f"PROCEED: Function {func.__name__} will not proceed")
    return False


def around_action(arg):
    print(
        "AROUND_ACTION: Function did not proceed, but around_action was called instead"
    )
    print(
        f"AROUND_ACTION: Doing something with value {arg} which was passed to around_action as an argument called arg"
    )

    return "new return value"


@Around(None, proceed, around_action, 15)
def test_around(test_text: str = "default"):
    """
    This docstring will be returned by test_around.__doc__
    because of @wraps(func) used in decorators.py
    """
    print(f"TEST_AROUND: Doing something {test_text} 4")
    return test_text


class MyClass(metaclass=Aspect):
    def test1(self):
        print("TEST 1: Doing something")
        return 1

    def test2(self):
        print("TEST 2: Doing something")
        return 2

    def test3(self):
        print("TEST 3: Doing something")
        return 3

    def test4(self):
        print("TEST 4: Doing something")
        return 4

    def test5(self):
        print("TEST 5: Doing something")
        return 6

    def test6(self):
        print("TEST 6: Doing something")
        return 7

    def test7(self, number, x: Any, y: Any=1) -> str:
        print(f"TEST 7 STR: Doing something with args: {number}, {x} and {y}")
        return "8"

    def test_7(self) -> int:
        print("TEST_7 INT: Doing something")
        return 8

    def test8(self):
        print("TEST 8: Doing something like throwing a ValueError")
        raise ValueError("ValueError thrown")

    def test9(self):
        print("TEST 9: Doing something like throwing a ConnectionError")
        raise ConnectionError("ConnectionError thrown")

    def test10(self):
        print("TEST 10: Doing something like throwing a NotImplementedError")
        raise NotImplementedError("NotImplementedError thrown")


print("------------------------BEFORE------------------------")

print(test_before("cool"))

print(f"__name__: {test_before.__name__}")

print(f"__doc__: {test_before.__doc__}\n")

print("--------------------AFTER-RETURNING-------------------")

print(f"Return value: {test_after_returning('cool')}")

print(f"__name__: {test_after_returning.__name__}")

print(f"__doc__: {test_after_returning.__doc__}\n")

print("------------AFTER-THROWING-WITH-EXCEPTION-------------")

print(f"Return value: {test_after_throwing('suspicious', throw=True)}\n")

print("----------AFTER-THROWING-WITHOUT-EXCEPTION------------")

print(f"Return value: {test_after_throwing('suspicious')}")

print(f"__name__: {test_after_throwing.__name__}")

print(f"__doc__: {test_after_throwing.__doc__}\n")

print("------------------------AROUND------------------------")

print(f"Return value: {test_around()}")

print(f"__name__: {test_around.__name__}")

print(f"__doc__: {test_around.__doc__}\n")

print("------------------------CLASS-------------------------")

my_class = MyClass()

print(f"Return value: {my_class.test1()}\n")
print(f"Return value: {my_class.test2()}\n")
print(f"Return value: {my_class.test3()}\n")
print(f"Return value: {my_class.test4()}\n")
print(f"Return value: {my_class.test5()}\n")
print(f"Return value: {my_class.test6()}\n")
print(f"Return value: {my_class.test7(4555, "x", y="y")}\n")
print(f"Return value: {my_class.test_7()}\n")
print(f"Return value: {my_class.test8()}\n")
print(f"Return value: {my_class.test9()}\n")
print(f"Return value: {my_class.test10()}\n")

print("------------------------END---------------------------")
