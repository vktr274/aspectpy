from inspect import signature
from typing import Any, Callable, Type
from functools import wraps

FLAG_CHECKED = "_AFTER_RETURNING_CHECKED_"


def after_returning_arg_check(func: Callable[..., Any]):
    """
    Decorator that checks if the action to be used in AfterReturning
    has the correct signature, i.e. has a parameter named "_RETURNED_VAL_".

    :param func: The action to be used in AfterReturning.
    :raises ValueError: If the action does not have a parameter named "_RETURNED_VAL_".
    :raises ValueError: If the action is already decorated with @after_returning_arg_check.
    :return: Wrapper function.
    """
    if hasattr(func, FLAG_CHECKED) and getattr(func, FLAG_CHECKED):
        raise ValueError(
            f"{func.__qualname__} is already decorated with @{after_returning_arg_check.__name__}"
        )
    setattr(func, FLAG_CHECKED, True)

    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = signature(func)
        arg_name = "_RETURNED_VAL_"

        if not sig.parameters:
            raise ValueError(
                f"{func.__qualname__} has no parameters. Missing '{arg_name}' argument at index 0."
            )

        if arg_name not in sig.parameters:
            raise ValueError(
                f"{func.__qualname__} is missing '{arg_name}' argument at index 0."
            )

        return func(*args, **kwargs)

    return wrapper


def mutate_kwargs(
    kwargs: dict[str, Any], new_kwargs: dict[str, Any] | None
) -> dict[str, Any]:
    """
    Updates the kwargs dictionary with the new kwargs dictionary.
    If the new kwargs dictionary is None, the original kwargs dictionary is returned.

    :param kwargs: The original kwargs dictionary.
    :param new_kwargs: The new kwargs dictionary.
    :return: The updated kwargs dictionary.
    """
    if new_kwargs is None:
        return kwargs
    return kwargs | new_kwargs


def mutate_args(
    args: tuple[Any, ...], new_args: dict[int, Any] | None
) -> tuple[Any, ...]:
    """
    Updates the args tuple with the new values from the new args dictionary.

    :param args: The original args tuple.
    :param new_args: The new args dictionary with index to value mappings.
    :raises IndexError: If the index of the new args dictionary is out of range for the args tuple.
    :return: The updated args tuple.
    """
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
    """
    Decorator that executes an action before the decorated function is called.

    :param args_update: The new args dictionary with index to value mappings.
        If None or empty, the original args dictionary is used.
    :param kwargs_update: The new kwargs dictionary with key to value mappings.
        If None or empty, the original kwargs dictionary is used.
    :param action: The action to be executed before the decorated function is called.
    :param action_args: The args to be passed to the action.
    :param action_kwargs: The kwargs to be passed to the action.
    :return: wrapper function after instance of this class is called.
    """

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
            args = mutate_args(args, self.args_update)
            kwargs = mutate_kwargs(kwargs, self.kwargs_update)
            self.action(*self.action_args, **self.action_kwargs)
            return func(*args, **kwargs)

        return wrapper


class AfterReturning:
    """
    Decorator that executes an action after the decorated function is called and returns.

    :param args_update: The new args dictionary with index to value mappings.
        If None or empty, the original args dictionary is used.
    :param kwargs_update: The new kwargs dictionary with key to value mappings.
        If None or empty, the original kwargs dictionary is used.
    :param action: The action to be executed after the decorated function is called and returns.
        This action must have a parameter named "_RETURNED_VAL_" and must be decorated with
        @after_returning_arg_check.
    :param action_args: The args to be passed to the action.
    :param action_kwargs: The kwargs to be passed to the action.
    :return: wrapper function after instance of this class is called.
    """

    def __init__(
        self,
        args_update: dict[int, Any] | None,
        kwargs_update: dict[str, Any] | None,
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        if not getattr(action, FLAG_CHECKED, False):
            raise ValueError(
                f"{action.__qualname__} is not decorated "
                + f"with @{after_returning_arg_check.__name__}",
            )
        self.args_update = args_update
        self.kwargs_update = kwargs_update
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args = mutate_args(args, self.args_update)
            kwargs = mutate_kwargs(kwargs, self.kwargs_update)
            result = func(*args, **kwargs)
            return self.action(result, *self.action_args, **self.action_kwargs)

        return wrapper


class AfterThrowing:
    """
    Decorator that executes an action after the decorated function is called and throws an exception.

    :param args_update: The new args dictionary with index to value mappings.
        If None or empty, the original args dictionary is used.
    :param kwargs_update: The new kwargs dictionary with key to value mappings.
        If None or empty, the original kwargs dictionary is used.
    :param exceptions: The exceptions that trigger the action.
        If None, all exceptions trigger the action.
    :param action: The action to be executed after the decorated function is called and throws an exception.
    :param action_args: The args to be passed to the action.
    :param action_kwargs: The kwargs to be passed to the action.
    :return: wrapper function after instance of this class is called.
    """

    def __init__(
        self,
        args_update: dict[int, Any] | None,
        kwargs_update: dict[str, Any] | None,
        exceptions: tuple[Type[Exception], ...] | Type[Exception] | None,
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        self.args_update = args_update
        self.kwargs_update = kwargs_update
        self.exceptions = exceptions or Exception
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args = mutate_args(args, self.args_update)
            kwargs = mutate_kwargs(kwargs, self.kwargs_update)
            try:
                return func(*args, **kwargs)
            except self.exceptions:
                return self.action(*self.action_args, **self.action_kwargs)

        return wrapper


class Around:
    """
    Decorator that executes an action instead of the decorated function if the proceed condition is met.
    Else, the decorated function is called.

    :param args_update: The new args dictionary with index to value mappings.
        If None or empty, the original args dictionary is used.
    :param kwargs_update: The new kwargs dictionary with key to value mappings.
        If None or empty, the original kwargs dictionary is used.
    :param proceed: The proceed condition. Can be a boolean or a callable that returns a boolean.
    :param action: The action to be executed instead of the decorated function if the proceed condition is met.
    :param action_args: The args to be passed to the action.
    :param action_kwargs: The kwargs to be passed to the action.
    :return: wrapper function after instance of this class is called.
    """

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
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            proceed = self.proceed
            if callable(proceed):
                proceed = proceed(func)
            if isinstance(proceed, bool) and proceed:
                args = mutate_args(args, self.args_update)
                kwargs = mutate_kwargs(kwargs, self.kwargs_update)
                return func(*args, **kwargs)
            return self.action(*self.action_args, **self.action_kwargs)

        return wrapper
