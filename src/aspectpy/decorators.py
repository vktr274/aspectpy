from typing import Any, Callable, Type
from functools import wraps


def update_kwargs(kwargs: dict[str, Any], new_kwargs: dict[str, Any]) -> dict[str, Any]:
    return kwargs | new_kwargs


def update_args(args: tuple[Any, ...], new_args: dict[int, Any]) -> tuple[Any, ...]:
    mutable_args = list(args)
    for key, value in new_args.items():
        mutable_args[key] = value
    return tuple(mutable_args)


class Before:
    def __init__(self, action: Callable[..., Any], *action_args, **action_kwargs):
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"BEFORE: {args} {kwargs}")
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
            print(f"AFTER RET: {args} {kwargs}")
            result = func(*args, **kwargs)
            self.action(*self.action_args, **self.action_kwargs)
            return result

        return wrapper


class AfterThrowing:
    def __init__(
        self,
        exceptions: tuple[Type[Exception], ...] | Type[Exception] | None,
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        self.action = action
        if exceptions is None:
            self.exceptions = (Exception,)
        elif not isinstance(exceptions, tuple):
            self.exceptions = (exceptions,)
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"AFTER THROW: {args} {kwargs}")
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
        **action_kwargs,
    ):
        self.proceed = proceed
        self.around_action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"AROUND: {args} {kwargs}")
            proceed = self.proceed
            if callable(proceed):
                proceed = proceed(func)
            if isinstance(proceed, bool) and proceed:
                return func(*args, **kwargs)
            return self.around_action(*self.action_args, **self.action_kwargs)

        return wrapper
