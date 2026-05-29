"""
A first look at attrs: declaratively define a class and let attrs
generate the boring methods (__init__, __repr__, __eq__) for you.

Docs: https://www.attrs.org/
"""
from IPython.core.display import display, HTML
from attrs import define, field, Factory, asdict


# `@define` is the modern attrs decorator. Annotated class attributes
# become fields. attrs writes __init__, __repr__, and __eq__ for you.
@define
class Book:
    title: str
    author: str
    pages: int = 0
    # Use Factory(...) for mutable defaults so each instance gets its own.
    tags: list[str] = Factory(list)


heading("1. A class with no boilerplate")
note("Defining a Book class with @define gives us an __init__ for free.")

moby = Book("Moby-Dick", "Herman Melville", pages=635, tags=["classic", "sea"])
hhgg = Book("The Hitchhiker's Guide", "Douglas Adams", pages=224)

# attrs provides a useful __repr__ automatically.
note(f"<code>repr(moby)</code> &rarr; <code>{moby!r}</code>")
note(f"<code>repr(hhgg)</code> &rarr; <code>{hhgg!r}</code>")

heading("2. Equality comes for free")
note(
    "Two instances with the same field values compare equal, "
    "without you writing __eq__."
)
twin = Book("Moby-Dick", "Herman Melville", pages=635, tags=["classic", "sea"])
note(f"moby == twin? <strong>{moby == twin}</strong>")
note(f"moby == hhgg? <strong>{moby == hhgg}</strong>")

heading("3. Turn an instance into a dict")
note(
    "<code>asdict()</code> recursively converts an attrs instance into "
    "a plain dictionary, ready for JSON or logging."
)
display(asdict(moby), append=True)
