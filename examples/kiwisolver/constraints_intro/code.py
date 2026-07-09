"""
A first look at kiwisolver: laying out two boxes side by side.

Cassowary lets you describe relationships ("this is left of that",
"these two are the same width") and lets the solver figure out
concrete numbers that satisfy them. See:
https://kiwisolver.readthedocs.io/en/latest/basis/constraints_definition.html
"""
from IPython.core.display import display, HTML

# Kiwi is the Python binding to the Cassowary constraint solver.
# It's the same engine that powers many GUI layout systems.
import kiwisolver as kiwi

# Variables represent unknown numbers. The solver will assign values
# to them when we ask it to.
left_a = kiwi.Variable("left_a")
right_a = kiwi.Variable("right_a")
left_b = kiwi.Variable("left_b")
right_b = kiwi.Variable("right_b")

# Build a solver and feed it constraints. Constraints are written
# with normal Python operators: ==, <=, >=.
solver = kiwi.Solver()

# The container spans 0..300. Box A starts at the left edge.
solver.addConstraint(left_a == 0)

# Box B sits 20 pixels to the right of box A.
solver.addConstraint(left_b == right_a + 20)

# Both boxes are the same width.
solver.addConstraint((right_a - left_a) == (right_b - left_b))

# Box B's right edge is at 300 (the container's right edge).
solver.addConstraint(right_b == 300)

# Each box must be at least 50 wide. Mark this as STRONG so it
# only kicks in if it doesn't conflict with REQUIRED constraints.
solver.addConstraint(
    ((right_a - left_a) >= 50) | "strong"
)

# Ask the solver to find a solution and read the values back.
solver.updateVariables()

heading("Two boxes, equal width, with a 20px gap")
note("The solver computed these positions:")
display(HTML(
    "<pre>"
    f"box A:  left = {left_a.value():.0f}, right = {right_a.value():.0f}\\n"
    f"box B:  left = {left_b.value():.0f}, right = {right_b.value():.0f}"
    "</pre>"
), append=True)
