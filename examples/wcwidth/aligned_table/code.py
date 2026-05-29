# Aligning a table of mixed-width text.
#
# `str.ljust()` pads to a number of *codepoints*, which produces ragged
# columns when the data contains wide CJK characters or combining marks.
# `wcwidth.ljust()` and friends pad to a number of *display cells*,
# which is what your eyes (and a monospace terminal) actually care about.

heading("A menu in three languages")
note(
    "Each row has a dish name and a price. We'll render the menu twice: "
    "first with the standard library's <code>str.ljust()</code>, then with "
    "<code>wcwidth.ljust()</code>."
)

menu = [
    ("Espresso",       "$3.00"),
    ("コーヒー",         "¥400"),
    ("café au lait",   "€4.50"),
    ("绿茶",            "¥25"),
    ("Pão de queijo",  "R$8"),
]

# Naive alignment using str.ljust on codepoints -- columns will be ragged.
naive_lines = [f"{name.ljust(16)} {price}" for name, price in menu]

# Width-aware alignment using wcwidth.ljust on display cells.
aware_lines = [f"{wcwidth.ljust(name, 16)} {price}" for name, price in menu]

display(HTML(
    "<h3>str.ljust() (ragged):</h3>"
    f"<pre style='background:#fee'>{chr(10).join(naive_lines)}</pre>"
    "<h3>wcwidth.ljust() (aligned):</h3>"
    f"<pre style='background:#efe'>{chr(10).join(aware_lines)}</pre>"
), append=True)

heading("Centering and right-justifying")
note(
    "<code>wcwidth.center()</code> and <code>wcwidth.rjust()</code> are "
    "drop-in replacements for the string methods of the same name."
)

banner_width = 24
for title in ["Menu", "メニュー", "café"]:
    centered = wcwidth.center(title, banner_width, "*")
    display(HTML(f"<pre>{centered}</pre>"), append=True)
