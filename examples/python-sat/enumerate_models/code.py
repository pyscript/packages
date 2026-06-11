# ---------------------------------------------------------------------
# Enumerating every satisfying assignment with enum_models().
# ---------------------------------------------------------------------
#
# Many problems aren't just "is there a solution?" but "what are all
# the solutions?". PySAT's `enum_models()` yields models one at a
# time, blocking each one internally so the next call returns a
# genuinely different assignment.

from pysat.formula import CNF
from pysat.solvers import Solver


heading("All ways to pack a 3-item picnic basket")
note(
    "Variables: 1 = sandwich, 2 = salad, 3 = cake. Constraints: "
    "the basket must contain a sandwich OR a salad, and you "
    "refuse to bring salad without cake."
)

picnic = CNF()
picnic.append([1, 2])     # sandwich OR salad
picnic.append([-2, 3])    # salad -> cake

items = {1: "sandwich", 2: "salad", 3: "cake"}

# Collect every model. For tiny formulas this is fine; for big ones
# you'd usually cap the count or stop early.
solutions = []
with Solver(name="glucose3", bootstrap_with=picnic.clauses) as solver:
    for model in solver.enum_models():
        chosen = tuple(items[v] for v in model if v > 0)
        solutions.append(chosen)

note(f"Total satisfying baskets: <strong>{len(solutions)}</strong>")

rows = "".join(
    f"<tr><td>{i + 1}</td><td>{', '.join(basket) or '(empty)'}</td></tr>"
    for i, basket in enumerate(solutions)
)
display(HTML(
    "<table border='1' cellpadding='6' cellspacing='0'>"
    "<tr><th>#</th><th>Basket contents</th></tr>"
    f"{rows}</table>"
), append=True)
