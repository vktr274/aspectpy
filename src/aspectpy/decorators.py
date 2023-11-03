from typing import Callable
from functools import wraps


class Before:
    def __init__(self, action_before: Callable, *action_args, **action_kwargs):
        self.action_before = action_before
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.action_before(*self.action_args, **self.action_kwargs)
            return func(*args, **kwargs)

        return wrapper


class AfterReturning:
    def __init__(self, after_returning_action: Callable, *action_args, **action_kwargs):
        self.after_returning_action = after_returning_action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            self.after_returning_action(*self.action_args, **self.action_kwargs)
            return result

        return wrapper


class AfterThrowing:
    def __init__(self, action_after_throwing: Callable, *action_args, **action_kwargs):
        self.action_after_throwing = action_after_throwing
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                self.action_after_throwing(*self.action_args, **self.action_kwargs)

        return wrapper


class Around:
    def __init__(
        self,
        proceed: bool | Callable[[Callable], bool],
        around_action: Callable,
        *action_args,
        **action_kwargs
    ):
        self.proceed = proceed
        self.around_action = around_action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            predicate = self.proceed
            if callable(predicate):
                predicate = predicate(func)
            if isinstance(predicate, bool) and predicate:
                return func(*args, **kwargs)
            return self.around_action(*self.action_args, **self.action_kwargs)

        return wrapper
