# ---------------------------------------------------------------------
# Cardinality encodings: "at most k of these literals are true".
# ---------------------------------------------------------------------
#
# Pure CNF can't directly say "at most one"; it has to be encoded as
# a bunch of binary clauses. PySAT's `pysat.card` does this for you
# with several well-known encodings.
#
# Classic warm-up: can you place N pigeons into N-1 holes such that
# each pigeon is in some hole and no hole holds more than one
# pigeon? The pigeonhole principle says no -- and the SAT solver
# will agree.

def pigeonhole(n_pigeons, n_holes):
    """Build a pigeonhole CNF and return (formula, var_map)."""
    pool = IDPool()
    # x[p, h] is true iff pigeon p sits in hole h.
    x = lambda p, h: pool.id(("x", p, h))

    formula = CNF()

    # Each pigeon must occupy at least one hole.
    for p in range(n_pigeons):
        formula.append([x(p, h) for h in range(n_holes)])

    # No hole can hold more than one pigeon: AtMost1 over each column.
    for h in range(n_holes):
        col = [x(p, h) for p in range(n_pigeons)]
        at_most_one = CardEnc.atmost(
            lits=col, bound=1, vpool=pool, encoding=EncType.pairwise,
        )
        formula.extend(at_most_one.clauses)

    return formula, x

heading("Pigeonhole: 4 pigeons into 3 holes")
formula, x = pigeonhole(n_pigeons=4, n_holes=3)
note(
    f"Encoded into <strong>{len(formula.clauses)}</strong> clauses "
    "over the original placement variables plus any auxiliaries "
    "introduced by the cardinality encoder."
)

with Solver(name="glucose3", bootstrap_with=formula.clauses) as solver:
    sat_4_3 = solver.solve()
note(f"4 pigeons, 3 holes satisfiable? <strong>{sat_4_3}</strong> (as expected).")

# Loosen the constraints: same number of holes as pigeons. Now there's
# plenty of room and we can read off a valid assignment.
heading("Pigeonhole: 4 pigeons into 4 holes")
formula, x = pigeonhole(n_pigeons=4, n_holes=4)

with Solver(name="glucose3", bootstrap_with=formula.clauses) as solver:
    sat_4_4 = solver.solve()
    model = set(solver.get_model() or [])

note(f"4 pigeons, 4 holes satisfiable? <strong>{sat_4_4}</strong>")

# Read the placement out of the model by checking each x(p, h) variable.
rows = []
for p in range(4):
    for h in range(4):
        if x(p, h) in model:
            rows.append(f"<tr><td>Pigeon {p}</td><td>Hole {h}</td></tr>")
            break

display(HTML(
    "<table border='1' cellpadding='6' cellspacing='0'>"
    "<tr><th>Pigeon</th><th>Assigned hole</th></tr>"
    f"{''.join(rows)}</table>"
), append=True)
