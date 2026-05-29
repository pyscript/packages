"""
A first taste of NLopt: minimize a smooth, gradient-based objective.

NLopt offers dozens of algorithms for nonlinear optimization,
both local and global, with or without constraints. The Python
interface revolves around a single object: `nlopt.opt(algorithm,
n_dims)`. You set bounds, an objective, stopping criteria, and
then call `optimize(x0)`.

Docs: https://nlopt.readthedocs.io/en/latest/NLopt_Python_Reference/
"""
from IPython.core.display import display, HTML

heading("Finding the bottom of a tilted bowl")
note(
    "We minimize f(x, y) = (x - 3)^2 + 2 * (y + 1)^2. "
    "The minimum is at (3, -1) with value 0. We use MMA, a "
    "gradient-based local algorithm, so the objective fills in "
    "<code>grad</code> in-place when NLopt asks for it."
)

# Track how many times the objective is called.
call_count = {"n": 0}


def bowl(x, grad):
    """Objective function with analytic gradient."""
    call_count["n"] += 1
    if grad.size > 0:
        # IMPORTANT: write into grad in place, do not rebind it.
        grad[0] = 2.0 * (x[0] - 3.0)
        grad[1] = 4.0 * (x[1] + 1.0)
    return (x[0] - 3.0) ** 2 + 2.0 * (x[1] + 1.0) ** 2


# LD_MMA = Local, Derivative-based, Method of Moving Asymptotes.
opt = nlopt.opt(nlopt.LD_MMA, 2)
opt.set_min_objective(bowl)
opt.set_lower_bounds([-10.0, -10.0])
opt.set_upper_bounds([10.0, 10.0])
opt.set_xtol_rel(1e-6)

x_star = opt.optimize([0.0, 0.0])
f_star = opt.last_optimum_value()

note(
    f"Found minimum at "
    f"<code>x = ({x_star[0]:.6f}, {x_star[1]:.6f})</code>, "
    f"with <code>f(x) = {f_star:.3e}</code>, "
    f"after <strong>{call_count['n']}</strong> objective evaluations."
)

# NLopt result codes are small positive integers on success.
note(f"Result code: {opt.last_optimize_result()} (positive means success).")
