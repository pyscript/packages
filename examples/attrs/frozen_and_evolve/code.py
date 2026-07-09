# ---------------------------------------------------------------------
# Immutable (frozen) classes are hashable and safer to share. Use
# evolve() to produce a modified copy without mutating the original.
# ---------------------------------------------------------------------

heading("Frozen classes: immutable, hashable, easy to copy")
note(
    "A <code>@frozen</code> class is the same as <code>@define</code> "
    "but its instances can't be modified after construction. That makes "
    "them safe to use as dict keys or set members."
)


@frozen
class Point:
    x: float
    y: float


origin = Point(0.0, 0.0)
target = Point(3.0, 4.0)

# Frozen instances are hashable, so we can put them in a set.
landmarks = {origin, target, Point(0.0, 0.0)}  # the duplicate is dropped
note(f"Unique landmarks in the set: <strong>{len(landmarks)}</strong>")

# Trying to mutate a frozen instance raises FrozenInstanceError.
try:
    target.x = 99.0
except attrs.exceptions.FrozenInstanceError as err:
    note(f"Mutation blocked: <strong>{type(err).__name__}</strong>")

heading("evolve(): make a tweaked copy")
note(
    "Since you can't mutate frozen instances, attrs gives you "
    "<code>evolve()</code> to build a new instance with some fields "
    "replaced. It works for non-frozen classes too."
)

shifted = evolve(target, x=target.x + 10)
note(f"Original: <code>{target!r}</code>")
note(f"Shifted:  <code>{shifted!r}</code>")

heading("Introspecting fields with attrs.fields()")
note(
    "Every attrs class carries metadata about its fields. This is the "
    "hook many libraries use to build serializers, forms, and CLIs."
)

for f in attrs.fields(Point):
    note(f"name=<code>{f.name}</code>, type=<code>{f.type}</code>, default=<code>{f.default}</code>")
