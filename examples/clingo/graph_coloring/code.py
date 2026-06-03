# ---------------------------------------------------------------------
# Graph coloring: assign one of K colors to each node so that no two
# adjacent nodes share a color. This is the classic "choice rule +
# integrity constraint" pattern in ASP.
# ---------------------------------------------------------------------

import clingo
from clingo.control import Control
from clingo.symbol import Number, Function, String


heading("Coloring a small map of regions")
note(
    "Six regions border each other in a fixed pattern. We ask clingo "
    "to color them with three colors so that no two neighbors share "
    "a color. The choice rule <code>1 { color(N,C) : col(C) } 1</code> "
    "means: pick exactly one color per node."
)

# Define the graph: nodes are regions, edges are shared borders.
edges = [
    ("north", "east"),
    ("north", "west"),
    ("east", "south"),
    ("west", "south"),
    ("south", "central"),
    ("central", "north"),
    ("central", "far"),
    ("far", "east"),
]

# Build the program. We pass the graph as facts, and let clingo handle
# the search over colorings.
node_facts = "\n".join(f"node({n})." for edge in edges for n in edge)
edge_facts = "\n".join(f"edge({a},{b})." for a, b in edges)

program = f"""
{node_facts}
{edge_facts}

col(red). col(green). col(blue).

% Choice rule: each node gets exactly one color.
1 {{ color(N, C) : col(C) }} 1 :- node(N).

% Integrity constraint: forbid adjacent nodes sharing a color.
:- color(A, C), color(B, C), edge(A, B).
"""

control = Control(["--models=5"])  # cap to first 5 solutions
control.add("base", [], program)
control.ground([("base", [])])

solutions = []

def on_model(model):
    coloring = {}
    for atom in model.symbols(atoms=True):
        if atom.name == "color" and len(atom.arguments) == 2:
            node, color = atom.arguments
            coloring[node.name] = color.name
    solutions.append(coloring)

result = control.solve(on_model=on_model)

note(f"Solver result: <code>{result}</code>. "
     f"Showing up to {len(solutions)} valid colorings.")

# Render each coloring as a small HTML table with colored cells.
swatch = {"red": "#e74c3c", "green": "#27ae60", "blue": "#3498db"}

for i, coloring in enumerate(solutions, start=1):
    rows = "".join(
        f'<tr><td style="padding:4px 10px;">{node}</td>'
        f'<td style="background:{swatch[c]};color:white;'
        f'padding:4px 10px;border-radius:3px;">{c}</td></tr>'
        for node, c in sorted(coloring.items())
    )
    display(HTML(f"<h4>Solution {i}</h4><table>{rows}</table>"), append=True)
