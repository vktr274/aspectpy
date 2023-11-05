from typing import Any, Callable, Type
from functools import wraps


def mutate_kwargs(
    kwargs: dict[str, Any], new_kwargs: dict[str, Any] | None
) -> dict[str, Any]:
    if new_kwargs is None:
        return kwargs
    return kwargs | new_kwargs


def mutate_args(
    args: tuple[Any, ...], new_args: dict[int, Any] | None
) -> tuple[Any, ...]:
    if new_args is None:
        return args
    mutable_args = list(args)
    for key, value in new_args.items():
        if key >= len(mutable_args):
            raise IndexError(
                f"Index {key} is out of range for the tuple of arguments of length {len(mutable_args)}"
            )
        mutable_args[key] = value
    return tuple(mutable_args)


class Before:
    def __init__(
        self,
        args_update: dict[int, Any] | None,
        kwargs_update: dict[str, Any] | None,
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        self.args_update = args_update
        self.kwargs_update = kwargs_update
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"BEFORE: {args} {kwargs}")
            args = mutate_args(args, self.args_update)
            kwargs = mutate_kwargs(kwargs, self.kwargs_update)
            self.action(*self.action_args, **self.action_kwargs)
            return func(*args, **kwargs)

        return wrapper


class AfterReturning:
    def __init__(
        self,
        args_update: dict[int, Any] | None,
        kwargs_update: dict[str, Any] | None,
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        self.args_update = args_update
        self.kwargs_update = kwargs_update
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"AFTER RET: {args} {kwargs}")
            args = mutate_args(args, self.args_update)
            kwargs = mutate_kwargs(kwargs, self.kwargs_update)
            result = func(*args, **kwargs)
            self.action(*self.action_args, **self.action_kwargs)
            return result

        return wrapper


class AfterThrowing:
    def __init__(
        self,
        args_update: dict[int, Any] | None,
        kwargs_update: dict[str, Any] | None,
        exceptions: tuple[Type[Exception], ...] | Type[Exception] | None,
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        if exceptions is None:
            self.exceptions = (Exception,)
        elif not isinstance(exceptions, tuple):
            self.exceptions = (exceptions,)
        self.args_update = args_update
        self.kwargs_update = kwargs_update
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"AFTER THROW: {args} {kwargs}")
            args = mutate_args(args, self.args_update)
            kwargs = mutate_kwargs(kwargs, self.kwargs_update)
            try:
                return func(*args, **kwargs)
            except self.exceptions:
                return self.action(*self.action_args, **self.action_kwargs)

        return wrapper


class Around:
    def __init__(
        self,
        args_update: dict[int, Any] | None,
        kwargs_update: dict[str, Any] | None,
        proceed: bool | Callable[[Callable[..., Any]], bool],
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        self.args_update = args_update
        self.kwargs_update = kwargs_update
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
                args = mutate_args(args, self.args_update)
                kwargs = mutate_kwargs(kwargs, self.kwargs_update)
                return func(*args, **kwargs)
            return self.around_action(*self.action_args, **self.action_kwargs)

        return wrapper
