from inspect import Signature, signature
from typing import Any, Callable, Type
from functools import wraps

FLAG_VALIDATED = "_AFTER_RETURNING_ACTION_VALIDATED_"


def validate_after_returning_action(func: Callable[..., Any]):
    """
    Decorator that checks if the action to be used in `AfterReturning`
    has the correct signature, i.e. has a parameter named `_RETURNED_VAL_`.

    Parameters
    ----------
    func : Callable
        The action to be used in `AfterReturning`.

    Returns
    -------
    Callable
        Wrapper function.

    Raises
    ------
    ValueError
        If the action does not have a parameter named `_RETURNED_VAL_`.
    ValueError
        If the action is already decorated with this decorator.
    """

    if hasattr(func, FLAG_VALIDATED) and getattr(func, FLAG_VALIDATED):
        raise ValueError(
            f"{func.__qualname__} is already decorated with @{validate_after_returning_action.__name__}"
        )
    setattr(func, FLAG_VALIDATED, True)

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


def mutate_params(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    new_params: dict[str, Any] | None,
    func_signature: Signature,
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    """
    Mutates arguments and keyword arguments with new parameters. If the update is
    executed, the `args` tuple gets emptied, and the `kwargs` dictionary gets filled
    with all the updated, new, or original parameters if some are missing from the
    `new_params` dictionary. Effectively, this decision does not affect code
    functionality, but rather is just a design choice. It allows for the arguments
    and keyword arguments to be updated by name, and the result is that every parameter
    becomes a keyword argument.

    Parameters
    ----------
    args : tuple
        The original arguments.

    kwargs : dict
        The original keyword arguments.

    new_params : dict or None
        Dictionary with key to value mappings representing new parameters.
        If `None` or empty, the original parameters are used.

        Can include both arguments and keyword arguments as
        `new_params[arg_name] = value` and `new_params[kwarg_name] = value`
        respectively.

    func_signature : Signature
        The signature of the function.

    Returns
    -------
    tuple
        Tuple of arguments and keyword arguments after mutation.
    """

    if new_params is None:
        return args, kwargs

    bound = func_signature.bind(*args, **kwargs)
    bound.apply_defaults()
    args = tuple()
    kwargs = bound.arguments

    for key, value in new_params.items():
        kwargs[key] = value
    return args, kwargs


class Before:
    """
    Decorator that executes an action before the decorated function is called.

    Parameters
    ----------
    params_update : dict or None
        Dictionary with key to value mappings representing new parameters.
        If `None` or empty, the original parameters are used.

        Can include both arguments and keyword arguments as
        `new_params[arg_name] = value` and `new_params[kwarg_name] = value`
        respectively.

    action : Callable
        The action to be executed before the decorated function is called.

    action_args : tuple
        The arguments to be passed to the action.

    action_kwargs : dict
        The keyword arguments to be passed to the action.

    Returns
    -------
    Callable
        Wrapper function after instance of this class is called.
    """

    def __init__(
        self,
        params_update: dict[str, Any] | None,
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        self.params_update = params_update
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args, kwargs = mutate_params(
                args, kwargs, self.params_update, signature(func)
            )
            self.action(*self.action_args, **self.action_kwargs)
            return func(*args, **kwargs)

        return wrapper


class AfterReturning:
    """
    Decorator that executes an action after the decorated function is called and returns.

    Parameters
    ----------
    params_update : dict or None
        Dictionary with key to value mappings representing new parameters.
        If `None` or empty, the original parameters are used.

        Can include both arguments and keyword arguments as
        `new_params[arg_name] = value` and `new_params[kwarg_name] = value`
        respectively.

    action : Callable
        The action to be executed after the decorated function is called and returns.
        This action must have a parameter named `_RETURNED_VAL_` and must be decorated with
        `@validate_after_returning_action`.

    action_args : tuple
        The arguments to be passed to the action.

    action_kwargs : dict
        The keyword arguments to be passed to the action.

    Returns
    -------
    Callable
        Wrapper function after instance of this class is called.
    """

    def __init__(
        self,
        params_update: dict[str, Any] | None,
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        if not getattr(action, FLAG_VALIDATED, False):
            raise ValueError(
                f"{action.__qualname__} is not decorated "
                + f"with @{validate_after_returning_action.__name__}",
            )
        self.params_update = params_update
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args, kwargs = mutate_params(
                args, kwargs, self.params_update, signature(func)
            )
            result = func(*args, **kwargs)
            return self.action(result, *self.action_args, **self.action_kwargs)

        return wrapper


class AfterThrowing:
    """
    Decorator that executes an action after the decorated function is called and throws an exception.

    Parameters
    ----------
    params_update : dict or None
        Dictionary with key to value mappings representing new parameters.
        If `None` or empty, the original parameters are used.

        Can include both arguments and keyword arguments as
        `new_params[arg_name] = value` and `new_params[kwarg_name] = value`
        respectively.

    exceptions : Exception or tuple of Exceptions or None
        The exceptions that trigger the action. If `None`, all exceptions trigger the action.

    action : Callable
        The action to be executed after the decorated function is called and throws an exception.

    action_args : tuple
        The arguments to be passed to the action.

    action_kwargs : dict
        The keyword arguments to be passed to the action.

    Returns
    -------
    Callable
        Wrapper function after instance of this class is called.
    """

    def __init__(
        self,
        params_update: dict[str, Any] | None,
        exceptions: tuple[Type[Exception], ...] | Type[Exception] | None,
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        self.params_update = params_update
        self.exceptions = exceptions or Exception
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args, kwargs = mutate_params(
                args, kwargs, self.params_update, signature(func)
            )
            try:
                return func(*args, **kwargs)
            except self.exceptions:
                return self.action(*self.action_args, **self.action_kwargs)

        return wrapper


class Around:
    """
    Decorator that executes an action instead of the decorated function if the proceed condition is met.
    Else, the decorated function is called.

    Parameters
    ----------
    params_update : dict or None
        Dictionary with key to value mappings representing new parameters.
        If `None` or empty, the original parameters are used.

        Can include both arguments and keyword arguments as
        `new_params[arg_name] = value` and `new_params[kwarg_name] = value`
        respectively.

    proceed : bool or Callable
        The proceed condition. Can be a boolean or a callable that returns a boolean.

    action : Callable
        The action to be executed instead of the decorated function if the proceed condition is met.

    action_args : tuple
        The arguments to be passed to the action.

    action_kwargs : dict
        The keyword arguments to be passed to the action.

    Returns
    -------
    Callable
        Wrapper function after instance of this class is called.
    """

    def __init__(
        self,
        params_update: dict[str, Any] | None,
        proceed: bool | Callable[[Callable[..., Any]], bool],
        action: Callable[..., Any],
        *action_args,
        **action_kwargs,
    ):
        self.params_update = params_update
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
                args, kwargs = mutate_params(
                    args, kwargs, self.params_update, signature(func)
                )
                return func(*args, **kwargs)
            return self.action(*self.action_args, **self.action_kwargs)

        return wrapper
