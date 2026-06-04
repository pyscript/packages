# ---------------------------------------------------------------------
# Constraint strengths: required, strong, medium, weak.
# ---------------------------------------------------------------------
#
# When constraints conflict, kiwi uses strengths to decide which
# ones win. REQUIRED constraints must hold; the others are honored
# in order of strength, with weaker ones giving way first.

import kiwisolver as kiwi


heading("Picking a font size that fits")
note(
    "We want a heading to be 24pt, but it must also fit inside a "
    "container of a given width without going below 10pt. The "
    "preferred size is a soft wish; the bounds are hard rules."
)

font_size = kiwi.Variable("font_size")
container_width = kiwi.Variable("container_width")

# Roughly: each point of font size needs ~7 pixels of width for our
# label. So font_size * 7 must fit inside container_width.
solver = kiwi.Solver()
solver.addConstraint(font_size >= 10)                        # required
solver.addConstraint(font_size <= 72)                        # required
solver.addConstraint((font_size * 7) <= container_width)     # required

# Soft preferences: ideally 24pt, but if we have to shrink, do so
# gently. STRONG beats WEAK when both can't be satisfied.
solver.addConstraint((font_size == 24) | "strong")
solver.addConstraint((font_size == 18) | "weak")

solver.addEditVariable(container_width, "strong")

note("Watch the chosen font size as the container shrinks:")

results = []
for w in [400, 250, 160, 100, 60]:
    solver.suggestValue(container_width, w)
    solver.updateVariables()
    results.append((w, font_size.value()))

rows_html = "".join(
    f"<tr><td>{w} px</td><td>{fs:.1f} pt</td></tr>"
    for w, fs in results
)
display(HTML(
    "<table border='1' cellpadding='6' style='border-collapse:collapse'>"
    "<tr><th>container width</th><th>chosen font size</th></tr>"
    f"{rows_html}</table>"
), append=True)

note(
    "At 400 px the strong preference wins and we get 24 pt. As space "
    "tightens, the required upper bound on width forces the size down, "
    "but never below the required minimum of 10 pt."
)

heading("Custom strengths")
note(
    "You can also build custom strengths from the three weight "
    "components (strong, medium, weak). Higher numbers dominate."
)

# kiwi.strength.create(strong, medium, weak[, multiplier]) returns
# a numeric strength you can attach to a constraint with `|`.
prefer_even = kiwi.strength.create(0, 1, 0)   # medium
prefer_round = kiwi.strength.create(0, 0, 5)  # weak, but heavier weak

x = kiwi.Variable("x")
s2 = kiwi.Solver()
s2.addConstraint(x >= 0)
s2.addConstraint(x <= 100)
s2.addConstraint((x == 42) | prefer_even)
s2.addConstraint((x == 50) | prefer_round)
s2.updateVariables()

note(
    f"With a medium preference for 42 and a weak preference for 50, "
    f"the solver picks <strong>x = {x.value():.0f}</strong>."
)
