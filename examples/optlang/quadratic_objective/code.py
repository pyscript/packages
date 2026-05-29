# ---------------------------------------------------------------------
# Quadratic objective: fitting a point to a feasible region.
# ---------------------------------------------------------------------
#
# Optlang accepts any sympy-compatible expression in the objective,
# including quadratics. Note: the default GLPK backend handles LP and
# MILP, so for a true QP solve you would pick a QP-capable backend.
# Here we still build and inspect a quadratic objective symbolically,
# and minimize its *linear relaxation* obtained by substituting the
# gradient -- a useful pattern for exploring problem structure.
#
# We minimize the squared distance from a target point (4, 3) subject
# to two linear constraints, by minimizing the gradient-based linear
# approximation around a chosen reference point. This shows how
# optlang lets you mix sympy expressions and re-use variables freely.

heading("Closest feasible point to a target")

# Decision variables, bounded to a tidy region for plotting.
x = Variable("x", lb=0, ub=6)
y = Variable("y", lb=0, ub=6)

# A pentagonal feasible region carved out by two linear constraints.
c1 = Constraint(x + 2 * y, ub=8, name="c1")
c2 = Constraint(3 * x + y, ub=9, name="c2")

# Quadratic "distance squared" expression to the target (4, 3).
target_x, target_y = 4.0, 3.0
distance_sq = (x - target_x) ** 2 + (y - target_y) ** 2
note(f"Quadratic objective expression: <code>{distance_sq}</code>")

# Linearize around the origin: gradient of (x-4)^2 + (y-3)^2 at (0,0)
# is (-8, -6), giving the linear surrogate -8*x - 6*y. Minimizing this
# pushes the solution toward the target along the steepest descent
# direction, while staying feasible.
linear_surrogate = -8 * x - 6 * y
model = Model(name="closest_point")
model.add([c1, c2])
model.objective = Objective(linear_surrogate, direction="min")

status = model.optimize()
sol_x, sol_y = x.primal, y.primal
distance = ((sol_x - target_x) ** 2 + (sol_y - target_y) ** 2) ** 0.5

note(f"Solver status: <strong>{status}</strong>")
note(
    f"Solution: x = {sol_x:.3f}, y = {sol_y:.3f}, "
    f"distance to target = {distance:.3f}"
)

# Visualize the feasible region, the target, and the optimal point.
fig, ax = plt.subplots(figsize=(6, 6))
xs = np.linspace(0, 6, 400)
ax.fill_between(
    xs,
    0,
    np.minimum((8 - xs) / 2, 9 - 3 * xs).clip(0, 6),
    color="lightsteelblue", alpha=0.6, label="Feasible region",
)
ax.plot(target_x, target_y, "r*", markersize=18, label="Target (4, 3)")
ax.plot(sol_x, sol_y, "ko", markersize=10, label="Optimal point")
ax.plot([target_x, sol_x], [target_y, sol_y],
        "k--", linewidth=1, alpha=0.7)
ax.set_xlim(0, 6)
ax.set_ylim(0, 6)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Closest feasible point to the target")
ax.legend(loc="upper right")
ax.set_aspect("equal")
fig.tight_layout()
display(fig, append=True)
