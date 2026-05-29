# ---------------------------------------------------------------------
# A mixed-integer transport problem: shipping cases between cities.
# ---------------------------------------------------------------------
#
# Two warehouses (Seattle, San Diego) ship to three stores (New York,
# Chicago, Topeka). We minimize total freight cost while respecting
# warehouse supply and store demand. Forcing variables to integer type
# turns this into a MILP, solved automatically by GLPK.

heading("Shipping cases from warehouses to stores")

supply = {"Seattle": 350, "San_Diego": 600}
demand = {"New_York": 325, "Chicago": 300, "Topeka": 275}

# Distances in thousands of miles, freight cost is $9 per case-kmile.
distances = {
    "Seattle":   {"New_York": 2.5, "Chicago": 1.7, "Topeka": 1.8},
    "San_Diego": {"New_York": 2.5, "Chicago": 1.8, "Topeka": 1.4},
}
freight_cost = 9

# One integer variable per (origin, destination) lane.
shipments = {}
for origin in supply:
    shipments[origin] = {}
    for destination in demand:
        shipments[origin][destination] = Variable(
            name=f"{origin}_to_{destination}", lb=0, type="integer",
        )

# Supply constraints: each warehouse ships at most its stock.
constraints = []
for origin in supply:
    constraints.append(Constraint(
        sum(shipments[origin].values()),
        ub=supply[origin],
        name=f"{origin}_supply",
    ))

# Demand constraints: each store receives at least what it needs.
for destination in demand:
    constraints.append(Constraint(
        sum(row[destination] for row in shipments.values()),
        lb=demand[destination],
        name=f"{destination}_demand",
    ))

# Objective: minimize total freight cost across all lanes.
objective = Objective(
    sum(
        freight_cost * distances[o][d] * shipments[o][d]
        for o in supply for d in demand
    ),
    direction="min",
)

model = Model(name="transport")
model.add(constraints)
model.objective = objective

status = model.optimize()
note(f"Solver status: <strong>{status}</strong>")
note(f"Minimum freight cost: <strong>${model.objective.value:.2f}</strong>")

# Lay out the optimal shipping plan as an origin-by-destination table.
header = "<tr><th>From \\ To</th>" + "".join(
    f"<th>{d}</th>" for d in demand
) + "</tr>"
body_rows = []
for o in supply:
    cells = "".join(
        f"<td>{int(shipments[o][d].primal)}</td>" for d in demand
    )
    body_rows.append(f"<tr><th>{o}</th>{cells}</tr>")
display(HTML("<table>" + header + "".join(body_rows) + "</table>"),
        append=True)
