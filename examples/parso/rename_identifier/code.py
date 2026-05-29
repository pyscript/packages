# ---------------------------------------------------------------------
# Round-trip parsing means we can change a single leaf in the tree and
# get back the original source with just that change applied -- all
# whitespace, comments and formatting are preserved exactly.
# ---------------------------------------------------------------------

heading("Renaming a variable while keeping formatting intact")
note(
    "We'll rename every occurrence of <code>tmp</code> to "
    "<code>buffer</code> in this snippet by walking the tree's "
    "leaves and rewriting matching Name tokens."
)

source = """\
def normalize(values):
    # Scale values into the unit interval.
    tmp = max(values)        # peak value
    if tmp == 0:
        return values
    return [v / tmp for v in values]   # divide each by the peak
"""

display(HTML(f"<pre style='background:#f6f8fa;padding:8px'>{source}</pre>"), append=True)

module = parso.parse(source)


def walk_leaves(node):
    """Yield every leaf (token) in the tree, in source order."""
    if hasattr(node, "children"):
        for child in node.children:
            yield from walk_leaves(child)
    else:
        yield node


# Mutate matching Name leaves directly. The tree remembers the
# surrounding whitespace via each leaf's `prefix`, so get_code()
# stitches everything back together untouched.
renamed = 0
for leaf in walk_leaves(module):
    if leaf.type == "name" and leaf.value == "tmp":
        leaf.value = "buffer"
        renamed += 1

note(f"Rewrote <strong>{renamed}</strong> occurrence(s) of <code>tmp</code>:")
display(
    HTML(
        f"<pre style='background:#eef7ee;padding:8px'>{module.get_code()}</pre>"
    ),
    append=True,
)

heading("Why this works")
note(
    "Each leaf carries its <code>value</code> (the token text) and a "
    "<code>prefix</code> (whitespace and comments preceding it). "
    "Editing only <code>value</code> leaves comments, indentation, and "
    "blank lines exactly where they were -- the foundation parso lays "
    "for refactoring tools."
)
