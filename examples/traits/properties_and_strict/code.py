# ---------------------------------------------------------------------
# Section 3: Computed values via Property, plus HasStrictTraits to lock
# the class down so typos become errors.
# ---------------------------------------------------------------------

heading("Properties: traits computed from other traits")
note(
    "A <code>Property</code> trait derives its value from other traits. "
    "Mark its getter with <code>@cached_property</code> and declare what "
    "it depends on with <code>observe=...</code>; the cache is "
    "invalidated automatically when any dependency changes."
)


class Rectangle(HasStrictTraits):
    """A rectangle with derived area and perimeter.

    HasStrictTraits forbids assignment to undeclared attributes, so a
    typo like ``rect.with = 5`` raises immediately instead of silently
    creating a stray attribute.
    """

    width = Float(1.0)
    height = Float(1.0)

    area = Property(Float, observe="width, height")
    perimeter = Property(Float, observe="width, height")

    @cached_property
    def _get_area(self):
        # Print so we can see when the getter actually runs.
        compute_log.append(f"computing area for {self.width} x {self.height}")
        return self.width * self.height

    @cached_property
    def _get_perimeter(self):
        compute_log.append(
            f"computing perimeter for {self.width} x {self.height}"
        )
        return 2 * (self.width + self.height)


compute_log = []
rect = Rectangle(width=3.0, height=4.0)

# Repeated reads use the cache; the getter only runs once per change.
values = [rect.area, rect.area, rect.perimeter, rect.perimeter]
note(f"Read area twice, perimeter twice: {values}")
display(HTML("<pre>" + "\n".join(compute_log) + "</pre>"), append=True)

# Changing a dependency invalidates both cached properties.
compute_log.clear()
rect.width = 10.0
values = [rect.area, rect.perimeter]
note(f"After setting width=10, values are {values}. Recomputation log:")
display(HTML("<pre>" + "\n".join(compute_log) + "</pre>"), append=True)


heading("Strictness catches typos")
note(
    "Because Rectangle inherits from <code>HasStrictTraits</code>, "
    "assigning to a name that isn't a declared trait fails fast."
)
try:
    rect.heigth = 7.0   # note the typo
except Exception as exc:
    display(HTML(
        f"<pre>rect.heigth = 7.0  -> {type(exc).__name__}: {exc}</pre>"
    ), append=True)
