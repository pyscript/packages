"""
A first look at optlang: formulate and solve a small linear program.

Imagine a tiny workshop that builds three furniture kits (x1, x2, x3).
Each kit consumes different amounts of wood, labor, and finishing time,
and yields different profit. We want to maximize profit, subject to
limited supplies of each resource.

    maximize    10*x1 + 6*x2 + 4*x3
    subject to       x1 +    x2 +    x3 <= 100   (units of wood)
                10*x1 +  4*x2 +  5*x3 <= 600     (labor hours)
                 2*x1 +  2*x2 +  6*x3 <= 300     (finishing hours)
                 x1, x2, x3 >= 0

This is the classic GLPK example, recast as a workshop story.
Docs: https://optlang.readthedocs.io
"""
from IPython.core.display import display, HTML
from optlang import Model, Variable, Constraint, Objective


heading("A small workshop's production plan")
note(
    "We declare three non-negative variables, three resource "
    "constraints, and a profit objective, then solve the model."
)

# Variables: each is non-negative (lb=0). Names are arbitrary labels.
x1 = Variable("x1", lb=0)
x2 = Variable("x2", lb=0)
x3 = Variable("x3", lb=0)

# Constraints are built from symbolic expressions plus bounds.
wood = Constraint(x1 + x2 + x3, ub=100, name="wood")
labor = Constraint(10 * x1 + 4 * x2 + 5 * x3, ub=600, name="labor")
finishing = Constraint(2 * x1 + 2 * x2 + 6 * x3, ub=300, name="finishing")

# Objective: maximize profit.
profit = Objective(10 * x1 + 6 * x2 + 4 * x3, direction="max")

# Assemble the model. Variables get added implicitly via the
# constraints and objective that reference them.
model = Model(name="workshop")
model.objective = profit
model.add([wood, labor, finishing])

status = model.optimize()
note(f"Solver status: <strong>{status}</strong>")
note(f"Maximum profit: <strong>{model.objective.value:.2f}</strong>")

# Show the optimal production plan and how tight each constraint is.
rows = ["<tr><th>Kit</th><th>Quantity</th></tr>"]
for name, var in model.variables.items():
    rows.append(f"<tr><td>{name}</td><td>{var.primal:.2f}</td></tr>")
display(HTML("<table>" + "".join(rows) + "</table>"), append=True)

note("Resource usage at the optimum (primal value vs. upper bound):")
usage_rows = ["<tr><th>Resource</th><th>Used</th><th>Limit</th></tr>"]
for c in model.constraints:
    usage_rows.append(
        f"<tr><td>{c.name}</td><td>{c.primal:.2f}</td>"
        f"<td>{c.ub}</td></tr>"
    )
display(HTML("<table>" + "".join(usage_rows) + "</table>"), append=True)
