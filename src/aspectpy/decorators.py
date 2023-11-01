from typing import Callable
from functools import wraps


def before(action_before: Callable, *action_args, **action_kwargs):
    def advice(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            action_before(*action_args, **action_kwargs)
            return func(*args, **kwargs)

        return wrapper

    return advice


def after_returning(after_returning_action: Callable, *action_args, **action_kwargs):
    def advice(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            after_returning_action(*action_args, **action_kwargs)
            return result

        return wrapper

    return advice


def after_throwing(action_after_throwing: Callable, *action_args, **action_kwargs):
    def advice(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                action_after_throwing(*action_args, **action_kwargs)

        return wrapper

    return advice


def around(
    proceed: bool | Callable[[Callable], bool],
    around_action: Callable,
    *action_args,
    **action_kwargs
):
    def advice(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            predicate = proceed
            if callable(predicate):
                predicate = predicate(func)
            if predicate:
                return func(*args, **kwargs)
            return around_action(*action_args, **action_kwargs)

        return wrapper

    return advice
