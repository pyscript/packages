"""
A first look at the `deprecation` package.

The `@deprecation.deprecated` decorator gives you three things at once:
a clear warning when the function is called, an automatically-extended
docstring for your API docs, and a structured record of when the
function should be removed entirely.

See: http://deprecation.readthedocs.io/
"""
from IPython.core.display import display, HTML

# Pretend this is the version string of our library, e.g. from a
# `__version__` attribute. The decorator compares this to the
# `deprecated_in` and `removed_in` versions to decide what to do.
__version__ = "1.2.0"


@deprecation.deprecated(
    deprecated_in="1.0",
    removed_in="2.0",
    current_version=__version__,
    details="Use `area_of_circle` instead.",
)
def circle_area(radius):
    """Compute the area of a circle from its radius."""
    return 3.14159 * radius * radius


def area_of_circle(radius):
    """Compute the area of a circle (the supported replacement)."""
    return 3.14159 * radius * radius


heading("1. The decorator extends the docstring")
note(
    "Notice the deprecation notice appended to the docstring. "
    "Tools like Sphinx autodoc will pick this up automatically."
)
display(HTML(f"<pre>{circle_area.__doc__}</pre>"), append=True)

heading("2. Calling the function emits a DeprecatedWarning")
note(
    "We use `warnings.catch_warnings` so we can capture and display "
    "the warning here. In a real app it would surface through Python's "
    "normal warnings machinery."
)

with warnings.catch_warnings(record=True) as captured:
    warnings.simplefilter("always")
    result = circle_area(5)

for w in captured:
    note(
        f"<strong>{w.category.__name__}:</strong> "
        f"{w.message}"
    )
note(f"The function still returns its result: <code>{result}</code>")
