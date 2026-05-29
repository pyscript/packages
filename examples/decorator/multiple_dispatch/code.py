# ---------------------------------------------------------------------
# Section 3: Multiple dispatch on the type of one argument.
# ---------------------------------------------------------------------

heading("3. Single-argument dispatch with `dispatch_on`")
note(
    "Beyond decorators, the package ships a small `dispatch_on` "
    "helper: register multiple implementations of a generic "
    "function and let the runtime pick one based on the type of "
    "a chosen argument. Think of a tiny shape library where "
    "`area(shape)` does the right thing for each shape type."
)


# Define the shape types we want to dispatch on.
class Shape:
    pass


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height


class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height


# `dispatch_on("shape")` declares that the implementation will be
# selected based on the runtime type of the `shape` argument.
@dispatch_on("shape")
def area(shape):
    """Return the area of a shape. Implementations registered below."""
    raise NotImplementedError(
        f"no area implementation for {type(shape).__name__}"
    )


@area.register(Circle)
def _(shape):
    from math import pi
    return pi * shape.radius ** 2


@area.register(Rectangle)
def _(shape):
    return shape.width * shape.height


@area.register(Triangle)
def _(shape):
    return 0.5 * shape.base * shape.height


# A mixed collection of shapes; `area` picks the right implementation.
shapes = [
    ("unit circle", Circle(radius=1)),
    ("A4 page (cm)", Rectangle(width=21, height=29.7)),
    ("right triangle", Triangle(base=3, height=4)),
    ("big circle", Circle(radius=10)),
]

heading("Computed areas")
for label, shape in shapes:
    note(
        f"<code>{type(shape).__name__}</code> &mdash; {label}: "
        f"area = <strong>{area(shape):.2f}</strong>"
    )

heading("Falling back when no implementation matches")
try:
    area(Shape())
except NotImplementedError as exc:
    note(f"Got expected error: <code>{exc}</code>")
