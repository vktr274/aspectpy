# AspectPy: Replicating AspectJ Constructs in Python

This project aims to replicate the functionality of AspectJ in Python. The chosen AspectJ constructs are `before()`, `after() returning`, `after() throwing`, and `around()` advice. These advice are implemented using Python decorators for functions and methods.

The `before()` advice is implemented as a decorator factory class called `Before`. Similarly, the `after() returning` and `after() throwing` advice are implemented as `AfterReturning` and `AfterThrowing` decorator factory classes, respectively. The `around()` advice is implemented as a decorator factory class called `Around`.

The goal is to make the implementation of these advice as customizable as possible. The advice are implemented in the [`decorators.py`](src/aspectpy/decorators.py) file. The paper related to this project can be found in the repository as [`aspectpy_paper.pdf`](aspectpy_paper.pdf).

## Documentation

### Before Advice

The `Before` decorator factory class is used to implement the `before()` advice.

#### Constructor of `Before`

The constructor for the `Before` class takes in the following parameters:

- params_update (dict or None): Dictionary with key to value mappings representing new parameters. If `None` or empty, the original parameters are used. Can include both arguments and keyword arguments as `new_params[arg_name] = value` and `new_params[kwarg_name] = value` respectively.
- action (Callable): The action to be executed before the decorated function is called.
- action_args (tuple): The arguments to be passed to the action.
- action_kwargs (dict): The keyword arguments to be passed to the action.

#### Example Usage of `Before`

```python
from aspectpy.decorators import Before


def action(a, b="example"):
    print(f"action({a}, {b})")


@Before({"original_x": 15}, action, "a")
def original_function(original_x: int, original_y="original_y"):
    print(f"original_function({original_x}, {original_y})")


original_function(10)
# will print:
#  "action(a, example)"
#  "original_function(15, original_y)"
```

### After Returning Advice

The `AfterReturning` decorator factory class is used to implement the `after() returning` advice.

#### Constructor of `AfterReturning`

The constructor for the `AfterReturning` class takes in the following parameters:

- params_update (dict or None): Dictionary with key to value mappings representing new parameters. If `None` or empty, the original parameters are used. Can include both arguments and keyword arguments as `new_params[arg_name] = value` and `new_params[kwarg_name] = value` respectively.
- action (Callable): The action to be executed after the decorated function is called and returns. This action must have a parameter named `_RETURNED_VAL_` and must be decorated with `@validate_after_returning_action`.
- action_args (tuple): The arguments to be passed to the action.
- action_kwargs (dict): The keyword arguments to be passed to the action.

#### Example Usage of `AfterReturning`

```python
from aspectpy.decorators import AfterReturning, validate_after_returning_action


@validate_after_returning_action
def action(_RETURNED_VAL_):
    print(f"action({_RETURNED_VAL_})")
    return _RETURNED_VAL_ # may or may not return the same value


@AfterReturning({"original_x": 15}, action)
def original_function(original_x: int, original_y="original_y"):
    print(f"original_function({original_x}, {original_y})")
    return "returned_val"


original_function(10)
# will print:
#  "original_function(15, original_y)"
#  "action(returned_val)"
```

### After Throwing Advice

The `AfterThrowing` decorator factory class is used to implement the `after() throwing` advice.

#### Constructor of `AfterThrowing`

The constructor for the `AfterThrowing` class takes in the following parameters:

- params_update (dict or None): Dictionary with key to value mappings representing new parameters. If `None` or empty, the original parameters are used. Can include both arguments and keyword arguments as `new_params[arg_name] = value` and `new_params[kwarg_name] = value` respectively.
- exceptions (Exception or tuple of Exceptions or None): The exceptions that trigger the action. If `None`, all exceptions trigger the action.
- action (Callable): The action to be executed after the decorated function is called and throws an exception.
- action_args (tuple): The arguments to be passed to the action.
- action_kwargs (dict): The keyword arguments to be passed to the action.

#### Example Usage of `AfterThrowing`

```python
from aspectpy.decorators import AfterThrowing


def action():
    print("Exception was thrown by original_function... Executing action!")


@AfterThrowing({"original_x": 15}, ValueError, action)
def original_function(original_x: int, original_y="original_y"):
    print(f"original_function({original_x}, {original_y})")
    raise ValueError("example")


original_function(10)
# will print:
#  "original_function(15, original_y)"
#  "Exception was thrown by original_function... Executing action!"
```

### Around Advice

The `Around` decorator factory class is used to implement the `around()` advice.

#### Constructor of `Around`

The constructor for the `Around` class takes in the following parameters:

- params_update (dict or None): Dictionary with key to value mappings representing new parameters. If `None` or empty, the original parameters are used. Can include both arguments and keyword arguments as `new_params[arg_name] = value` and `new_params[kwarg_name] = value` respectively.
- proceed (bool or Callable): The proceed condition. Can be a boolean or a callable that returns a boolean.
- action (Callable): The action to be executed instead of the decorated function if the proceed condition is met.
- action_args (tuple): The arguments to be passed to the action.
- action_kwargs (dict): The keyword arguments to be passed to the action.

#### Example Usage of `Around`

```python
from aspectpy.decorators import Around


def action():
    print("Executing action!")

@Around(None, False, action)
def original_function():
    print("original_function()")


original_function()
# will print:
#  "Executing action!"
```

### Metaclass Example

The [`meta.py`](src/aspectpy/meta.py) file contains an example of an aspect in the form of a metaclass. It makes use of regular expressions to match the names of methods to apply advice to. The aspect can then be applied to a class by using the `metaclass` keyword argument in the class definition. Such usage can be seen in the [`test.py`](src/test.py) file in the `MyClass` class.
