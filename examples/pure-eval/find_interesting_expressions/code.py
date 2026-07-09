# ---------------------------------------------------------------------
# Walk an entire AST and collect every sub-expression we can safely
# evaluate. This is the bread and butter of tools that annotate source
# code with live values, such as debuggers and tracebacks.
# ---------------------------------------------------------------------
import ast
from pure_eval import Evaluator, group_expressions


heading("Scanning a script for evaluatable expressions")
note(
    "We exec a small script to populate a namespace, then ask "
    "<code>pure_eval</code> to find every expression in the script "
    "whose value it can determine without running side-effecting "
    "code."
)

source = """
inventory = {"apples": 12, "pears": 7, "plums": 3}
total_fruit = sum(inventory.values())
favourite = "pears"
favourite_count = inventory[favourite]
"""

# Run the script so the names exist with real values.
namespace = {}
exec(source, namespace)

tree = ast.parse(source)
evaluator = Evaluator(namespace)

# find_expressions yields every (node, value) pair that pure_eval can
# safely resolve. The same expression may appear in several places,
# so we group equivalent nodes together for a tidier report.
rows = []
for nodes, value in group_expressions(evaluator.find_expressions(tree)):
    snippet = ast.unparse(nodes[0])
    rows.append((snippet, repr(value), len(nodes)))

# Render as a small HTML table so it's easy to read.
table = ["<table border='1' cellpadding='4' style='border-collapse:collapse'>"]
table.append(
    "<tr><th>Expression</th><th>Value</th><th>Occurrences</th></tr>"
)
for snippet, value_repr, count in rows:
    table.append(
        f"<tr><td><code>{snippet}</code></td>"
        f"<td><code>{value_repr}</code></td>"
        f"<td>{count}</td></tr>"
    )
table.append("</table>")
display(HTML("".join(table)), append=True)

heading("Filtering down to the interesting ones")
note(
    "<code>interesting_expressions_grouped</code> drops obvious "
    "things like literals and bare references whose name matches "
    "the value's <code>__name__</code>. What's left is the stuff a "
    "human reader would actually want to see annotated."
)

interesting = evaluator.interesting_expressions_grouped(tree)

lines = ["<ul>"]
for nodes, value in interesting:
    snippet = ast.unparse(nodes[0])
    lines.append(f"<li><code>{snippet}</code> = <code>{value!r}</code></li>")
lines.append("</ul>")
display(HTML("".join(lines)), append=True)
