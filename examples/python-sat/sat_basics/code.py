"""
A first taste of PySAT: build a CNF formula, hand it to a SAT solver,
and read off a satisfying assignment.

PySAT exposes many state-of-the-art SAT solvers behind a single,
uniform Python API. See https://pysathq.github.io for the full docs.

Variables in PySAT are positive integers (1, 2, 3, ...). A clause is
a list of literals; a negative integer means the negation of that
variable. A formula in conjunctive normal form (CNF) is a list of
clauses that must all be satisfied simultaneously.
"""
from IPython.core.display import display, HTML

# Three Boolean variables: 1 = "Alice attends",
# 2 = "Bob attends", 3 = "Carol attends".
# We want to pick a guest list satisfying these social constraints:
#   - At least one of Alice or Bob must come.
#   - Bob and Carol have a feud, so they can't both come.
#   - If Alice comes, Carol comes too (Alice -> Carol, i.e. -1 v 3).
party = CNF()
party.append([1, 2])      # Alice OR Bob
party.append([-2, -3])    # NOT Bob OR NOT Carol
party.append([-1, 3])     # NOT Alice OR Carol

heading("A tiny party-planning SAT problem")
note(
    "Three variables, three clauses. The solver finds a guest list "
    "consistent with every constraint."
)
note(f"Clauses: {party.clauses}")

# Glucose 3 is a fast, well-known CDCL solver bundled with PySAT.
# Pass `bootstrap_with` to load the formula in one go.
with Solver(name="glucose3", bootstrap_with=party.clauses) as solver:
    is_sat = solver.solve()
    model = solver.get_model() if is_sat else None

names = {1: "Alice", 2: "Bob", 3: "Carol"}
note(f"Satisfiable? <strong>{is_sat}</strong>")
note(f"Raw model (positive = true, negative = false): {model}")

if model:
    attending = [names[v] for v in model if v > 0]
    declined = [names[-v] for v in model if v < 0]
    note(f"Attending: <strong>{', '.join(attending) or '(none)'}</strong>")
    note(f"Not attending: {', '.join(declined) or '(none)'}")
