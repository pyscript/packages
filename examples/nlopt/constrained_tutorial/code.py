# ---------------------------------------------------------------------
# The classic NLopt tutorial problem: minimize sqrt(x2)
# subject to x2 >= (a*x1 + b)^3 for two pairs (a, b).
# ---------------------------------------------------------------------
import numpy as np
import nlopt
import matplotlib.pyplot as plt


heading("Constrained minimization with two cubic inequalities")
note(
    "Minimize <code>f(x) = sqrt(x2)</code> subject to "
    "<code>x2 &ge; (2*x1)^3</code> and "
    "<code>x2 &ge; (-x1 + 1)^3</code>. The known optimum is "
    "<code>(1/3, 8/27)</code> with value "
    "<code>sqrt(8/27) &approx; 0.5443</code>."
)


def objective(x, grad):
    if grad.size > 0:
        grad[0] = 0.0
        grad[1] = 0.5 / np.sqrt(x[1])
    return np.sqrt(x[1])


def cubic_constraint(x, grad, a, b):
    """NLopt expects constraints in the form g(x) <= 0."""
    if grad.size > 0:
        grad[0] = 3 * a * (a * x[0] + b) ** 2
        grad[1] = -1.0
    return (a * x[0] + b) ** 3 - x[1]


opt = nlopt.opt(nlopt.LD_MMA, 2)
opt.set_min_objective(objective)
opt.set_lower_bounds([-float("inf"), 0.0])
# Use lambdas to inject the (a, b) parameters into the constraint.
opt.add_inequality_constraint(lambda x, g: cubic_constraint(x, g, 2, 0), 1e-8)
opt.add_inequality_constraint(lambda x, g: cubic_constraint(x, g, -1, 1), 1e-8)
opt.set_xtol_rel(1e-6)

x_star = opt.optimize([1.234, 5.678])
f_star = opt.last_optimum_value()

note(
    f"Optimum at <code>x = ({x_star[0]:.5f}, {x_star[1]:.5f})</code>, "
    f"<code>f(x) = {f_star:.6f}</code>."
)

# Visualize the feasible region and the optimum.
x1 = np.linspace(-0.5, 1.0, 400)
upper_a = (2 * x1) ** 3
upper_b = (-x1 + 1) ** 3
feasible_lower = np.maximum(upper_a, upper_b)

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(x1, upper_a, "--", color="gray", label="$x_2 = (2 x_1)^3$")
ax.plot(x1, upper_b, ":", color="gray", label="$x_2 = (-x_1+1)^3$")
ax.fill_between(x1, feasible_lower, 1.5, color="lightblue",
                alpha=0.5, label="Feasible region")
ax.plot(x_star[0], x_star[1], "o", color="crimson",
        markersize=9, label=f"Optimum ({x_star[0]:.3f}, {x_star[1]:.3f})")
ax.set_xlim(-0.5, 1.0)
ax.set_ylim(0, 1.2)
ax.set_xlabel("$x_1$")
ax.set_ylabel("$x_2$")
ax.set_title("Feasible region and constrained optimum")
ax.legend(loc="upper right", fontsize=9)
fig.tight_layout()
display(fig, append=True)
