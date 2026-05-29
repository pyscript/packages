# ---------------------------------------------------------------------
# Beyond grad: jacobian (vector outputs) and hessian (second derivatives).
# ---------------------------------------------------------------------

heading("Jacobian of a vector-valued function")
note(
    "When a function returns a vector, the right object is its "
    "Jacobian matrix: row i, column j is &part;output_i / &part;input_j. "
    "Autograd's <code>jacobian</code> builds it for you."
)


def polar_to_cartesian(rt):
    """Map (radius, angle) to (x, y). Outputs a 2-vector."""
    r, theta = rt
    return np.array([r * np.cos(theta), r * np.sin(theta)])


jac_polar = jacobian(polar_to_cartesian)

point = np.array([2.0, np.pi / 4])
note(
    f"At (r, &theta;) = (2.0, &pi;/4), the Jacobian is:"
)
display(np.round(jac_polar(point), 4), append=True)

# ---------------------------------------------------------------------
# Hessian: the matrix of second partial derivatives. Useful for
# Newton-style optimization and for inspecting curvature.
# ---------------------------------------------------------------------

heading("Hessian of a scalar function")
note(
    "Rosenbrock's banana function is a classic optimization "
    "test case. Its Hessian tells us how curved the loss surface "
    "is at any point, and which directions are stiff vs. flat."
)


def rosenbrock(xy):
    """Rosenbrock's function: minimum at (1, 1) with value 0."""
    x, y = xy
    return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2


rosen_grad = grad(rosenbrock)
rosen_hess = hessian(rosenbrock)

at_minimum = np.array([1.0, 1.0])
near_minimum = np.array([0.5, 0.5])

note(
    f"Gradient at the minimum (1, 1): "
    f"{np.round(rosen_grad(at_minimum), 6).tolist()} (essentially zero)"
    f"<br>Gradient at (0.5, 0.5):           "
    f"{np.round(rosen_grad(near_minimum), 4).tolist()}"
)

note("Hessian at the minimum (1, 1):")
display(np.round(rosen_hess(at_minimum), 2), append=True)

# Visualize the loss landscape with gradient arrows.
xs = np.linspace(-1.5, 1.8, 60)
ys = np.linspace(-0.8, 2.2, 60)
X, Y = np.meshgrid(xs, ys)
Z = (1 - X) ** 2 + 100 * (Y - X ** 2) ** 2

# Sample a sparse grid of gradient vectors for the quiver plot.
xs_q = np.linspace(-1.4, 1.6, 12)
ys_q = np.linspace(-0.6, 2.0, 12)
Xq, Yq = np.meshgrid(xs_q, ys_q)
U = np.zeros_like(Xq)
V = np.zeros_like(Yq)
for i in range(Xq.shape[0]):
    for j in range(Xq.shape[1]):
        g = rosen_grad(np.array([Xq[i, j], Yq[i, j]]))
        # Negate (descent direction) and clip for visibility.
        U[i, j], V[i, j] = -g[0], -g[1]
norms = np.sqrt(U ** 2 + V ** 2) + 1e-9
U, V = U / norms, V / norms

fig, ax = plt.subplots(figsize=(7, 5))
ax.contourf(X, Y, np.log10(Z + 1e-3), levels=25, cmap="viridis")
ax.quiver(Xq, Yq, U, V, color="white", scale=30, width=0.003)
ax.plot(1, 1, "r*", markersize=15, label="minimum")
ax.set_title("Rosenbrock landscape with descent directions")
ax.legend()
fig.tight_layout()
display(fig, append=True)
