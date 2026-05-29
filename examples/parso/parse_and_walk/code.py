"""
A first look at parso: parse Python source into a syntax tree, then
walk the tree to discover what's inside.

Parso is the parser that powers Jedi. It produces a concrete syntax
tree that preserves every byte of the original source (whitespace,
comments, the lot), which makes it a great tool for refactoring,
linting, and code analysis. Docs: https://parso.readthedocs.io
"""
from IPython.core.display import display, HTML

# A small but realistic snippet of Python to chew on.
source = """\
import math

def area_of_circle(radius):
    \\"\\"\\"Return the area of a circle with the given radius.\\"\\"\\"
    return math.pi * radius ** 2

def area_of_square(side):
    return side * side
"""

heading("Parsing source into a module")
note(
    "parso.parse returns the root node of the syntax tree -- a "
    "Module. We can ask the tree to round-trip back to the exact "
    "source it was parsed from."
)

module = parso.parse(source)
note(f"Top-level node type: <code>{module.type}</code>")
note(f"Round-trip matches original: <strong>{module.get_code() == source}</strong>")

heading("Listing top-level function definitions")
note(
    "iter_funcdefs walks the module's direct children and yields "
    "each function definition node. Each node knows its name and "
    "where it lives in the source."
)

rows = []
for funcdef in module.iter_funcdefs():
    name = funcdef.name.value
    start_line, start_col = funcdef.start_pos
    end_line, end_col = funcdef.end_pos
    params = [p.name.value for p in funcdef.get_params()]
    rows.append(
        f"<tr><td><code>{name}</code></td>"
        f"<td>{', '.join(params) or '&mdash;'}</td>"
        f"<td>lines {start_line}&ndash;{end_line}</td></tr>"
    )

table = (
    "<table border='1' cellpadding='6' cellspacing='0'>"
    "<tr><th>Function</th><th>Parameters</th><th>Location</th></tr>"
    + "".join(rows)
    + "</table>"
)
display(HTML(table), append=True)
