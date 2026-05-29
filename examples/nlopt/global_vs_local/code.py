# ---------------------------------------------------------------------
# When the landscape has many local minima, derivative-free global
# algorithms shine. Here we use DIRECT-L on the Rastrigin function,
# a classic test problem with a forest of local minima.
# ---------------------------------------------------------------------

heading("Global optimization on the Rastrigin function")
note(
    "Rastrigin in 2D: "
    "<code>f(x) = 20 + sum(x_i^2 - 10 cos(2&pi; x_i))</code>. "
    "It has hundreds of local minima inside [-5.12, 5.12]^2, with "
    "the global minimum at the origin. A local gradient method "
    "started far from zero will get stuck; a global method finds it."
)


def rastrigin(x, grad):
    # Derivative-free algorithms call us with grad.size == 0,
    # so we don't need to fill it in.
    return 20.0 + np.sum(x * x - 10.0 * np.cos(2.0 * np.pi * x))


bounds = 5.12

# A naive local search from a poor starting point.
local_opt = nlopt.opt(nlopt.LN_NELDERMEAD, 2)
local_opt.set_min_objective(rastrigin)
local_opt.set_lower_bounds([-bounds, -bounds])
local_opt.set_upper_bounds([bounds, bounds])
local_opt.set_xtol_rel(1e-6)
x_local = local_opt.optimize([4.0, -3.5])
f_local = local_opt.last_optimum_value()

# DIRECT-L: a Lipschitzian global search that does not need
# gradients and respects bound constraints.
global_opt = nlopt.opt(nlopt.GN_DIRECT_L, 2)
global_opt.set_min_objective(rastrigin)
global_opt.set_lower_bounds([-bounds, -bounds])
global_opt.set_upper_bounds([bounds, bounds])
# Global methods need a stopping budget; cap evaluations.
global_opt.set_maxeval(2000)
x_global = global_opt.optimize([4.0, -3.5])
f_global = global_opt.last_optimum_value()

note(
    f"Local Nelder-Mead landed at "
    f"<code>({x_local[0]:.3f}, {x_local[1]:.3f})</code> "
    f"with <code>f = {f_local:.4f}</code>."
)
note(
    f"Global DIRECT-L landed at "
    f"<code>({x_global[0]:.3f}, {x_global[1]:.3f})</code> "
    f"with <code>f = {f_global:.4f}</code> (true minimum is 0)."
)

# Plot the landscape with both solutions.
grid = np.linspace(-bounds, bounds, 300)
gx, gy = np.meshgrid(grid, grid)
gz = 20.0 + (gx ** 2 - 10 * np.cos(2 * np.pi * gx)) \
    + (gy ** 2 - 10 * np.cos(2 * np.pi * gy))

fig, ax = plt.subplots(figsize=(7, 5.5))
mesh = ax.pcolormesh(gx, gy, gz, shading="auto", cmap="viridis")
ax.plot(x_local[0], x_local[1], "o", color="white",
        markeredgecolor="black", markersize=10, label="Local (Nelder-Mead)")
ax.plot(x_global[0], x_global[1], "*", color="red",
        markeredgecolor="black", markersize=16, label="Global (DIRECT-L)")
ax.set_title("Rastrigin landscape: local vs. global solver")
ax.set_xlabel("$x_1$")
ax.set_ylabel("$x_2$")
ax.legend(loc="upper right")
fig.colorbar(mesh, ax=ax, label="f(x)")
fig.tight_layout()
display(fig, append=True)
