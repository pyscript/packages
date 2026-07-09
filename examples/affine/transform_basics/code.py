"""
A first look at the `affine` package: building 2D affine transforms
and applying them to points.

An Affine matrix represents a 2D linear transformation followed by a
translation. You compose them with `*`, apply them to points with `*`,
and invert them with `~`. Documentation: https://github.com/rasterio/affine
"""
from IPython.core.display import display, HTML
from affine import Affine

heading("1. Building transforms with the class methods")
note(
    "The most common way to make an Affine is via one of the named "
    "constructors: <code>identity</code>, <code>translation</code>, "
    "<code>scale</code>, <code>rotation</code> (degrees), and "
    "<code>shear</code>. Printing one shows the top two rows of the "
    "augmented 3x3 matrix."
)

identity = Affine.identity()
shift = Affine.translation(10.0, 5.0)
zoom = Affine.scale(2.0)
spin = Affine.rotation(30.0)  # 30 degrees, counter-clockwise

for name, transform in [
    ("identity", identity),
    ("translation(10, 5)", shift),
    ("scale(2.0)", zoom),
    ("rotation(30°)", spin),
]:
    note(f"<strong>{name}</strong>")
    display(transform, append=True)

heading("2. Applying a transform to a point")
note(
    "Multiplying an Affine by an <code>(x, y)</code> tuple gives the "
    "transformed point. Here we move the point (1, 1) by (10, 5)."
)
moved = shift * (1.0, 1.0)
note(f"shift * (1, 1) = {moved}")

heading("3. Composing and inverting transforms")
note(
    "Transforms compose with <code>*</code>. Read right-to-left: the "
    "rightmost transform is applied first. The inverse is written "
    "<code>~</code>, and a transform times its inverse is the identity."
)
spin_then_shift = shift * spin
note("shift * spin (rotate first, then translate):")
display(spin_then_shift, append=True)

inverse = ~spin_then_shift
roundtrip = inverse * spin_then_shift * (3.0, 4.0)
note(
    f"Round-trip of (3, 4) through the transform and its inverse: "
    f"({roundtrip[0]:.6f}, {roundtrip[1]:.6f})"
)
