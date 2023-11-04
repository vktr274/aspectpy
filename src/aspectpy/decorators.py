from typing import Callable, Type
from functools import wraps


class Before:
    def __init__(self, action: Callable, *action_args, **action_kwargs):
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.action(*self.action_args, **self.action_kwargs)
            return func(*args, **kwargs)

        return wrapper


class AfterReturning:
    def __init__(self, action: Callable, *action_args, **action_kwargs):
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            self.action(*self.action_args, **self.action_kwargs)
            return result

        return wrapper


class AfterThrowing:
    def __init__(
        self,
        action_and_exceptions: tuple[Callable, tuple[Type[Exception]]] | Callable,
        *action_args,
        **action_kwargs
    ):
        if callable(action_and_exceptions):
            self.action = action_and_exceptions
            self.exceptions = (Exception,)
        else:
            self.action = action_and_exceptions[0]
            self.exceptions = action_and_exceptions[1]
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except self.exceptions:
                self.action(*self.action_args, **self.action_kwargs)

        return wrapper


class Around:
    def __init__(
        self,
        proceed: bool | Callable[[Callable], bool],
        action: Callable,
        *action_args,
        **action_kwargs
    ):
        self.proceed = proceed
        self.around_action = action
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
