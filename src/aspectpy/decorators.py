from typing import Any, Callable, Type
from functools import wraps


class Before:
    def __init__(self, action: Callable[..., Any], *action_args, **action_kwargs):
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.action(*self.action_args, **self.action_kwargs)
            return func(*args, **kwargs)

        return wrapper


class AfterReturning:
    def __init__(self, action: Callable[..., Any], *action_args, **action_kwargs):
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            self.action(*self.action_args, **self.action_kwargs)
            return result

        return wrapper


class AfterThrowing:
    def __init__(
        self,
        action_and_exceptions: tuple[Callable[..., Any], tuple[Type[Exception]]]
        | Callable[..., Any],
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

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except self.exceptions:
                return self.action(*self.action_args, **self.action_kwargs)

        return wrapper


class Around:
    def __init__(
        self,
        proceed: bool | Callable[[Callable[..., Any]], bool],
        action: Callable[..., Any],
        *action_args,
        **action_kwargs
    ):
        self.proceed = proceed
        self.around_action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            proceed = self.proceed
            if callable(proceed):
                proceed = proceed(func)
            if isinstance(proceed, bool) and proceed:
                return func(*args, **kwargs)
            return self.around_action(*self.action_args, **self.action_kwargs)

        return wrapper
