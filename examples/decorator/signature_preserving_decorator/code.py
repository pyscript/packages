"""
A first look at the `decorator` package.

The standard `functools.wraps` approach copies a function's name and
docstring, but the *signature* of the wrapper is still `(*args, **kw)`.
The `decorator` package preserves the original signature exactly, which
matters for introspection, IDE help, and frameworks that rely on
`inspect.signature`.

Docs: https://github.com/micheles/decorator/blob/master/docs/documentation.md
"""
import inspect
import functools
from decorator import decorator
from IPython.core.display import display, HTML

heading("1. Why use `decorator`?")
note(
    "Compare a hand-rolled `functools.wraps` decorator against one "
    "built with `@decorator`. Both preserve the name and docstring, "
    "but only the latter preserves the original call signature."
)


# A traditional decorator using functools.wraps.
def trace_with_wraps(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        return func(*args, **kw)
    return wrapper


# The same idea, written with the `decorator` package. The decorated
# function `func` becomes the first argument; the rest mirror the
# wrapped function's own arguments.
@decorator
def trace(func, *args, **kw):
    """Print the call, then delegate to the wrapped function."""
    call = ", ".join(
        [repr(a) for a in args]
        + [f"{k}={v!r}" for k, v in kw.items()]
    )
    note(f"<code>{func.__name__}({call})</code> called")
    return func(*args, **kw)


@trace_with_wraps
def greet_a(name, greeting="Hello"):
    """Return a friendly greeting."""
    return f"{greeting}, {name}!"


@trace
def greet_b(name, greeting="Hello"):
    """Return a friendly greeting."""
    return f"{greeting}, {name}!"


heading("Signatures side by side")
note(f"functools.wraps version: <code>greet_a{inspect.signature(greet_a)}</code>")
note(f"decorator version:&nbsp;&nbsp;&nbsp;<code>greet_b{inspect.signature(greet_b)}</code>")

heading("Calling the decorated functions")
display(greet_b("Ada"), append=True)
display(greet_b("Grace", greeting="Hi"), append=True)
