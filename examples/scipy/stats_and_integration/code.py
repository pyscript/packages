# ---------------------------------------------------------------------
# scipy.stats and scipy.integrate: compare two groups, then integrate.
# ---------------------------------------------------------------------

heading("A/B test: did the new checkout flow help?")
note(
    "Two groups of users see different checkout flows. We use "
    "scipy.stats to compare their order values with a t-test and "
    "to fit a normal distribution to each group."
)

# Synthesize order values (in dollars) for the two variants.
control = rng.normal(loc=42.0, scale=12.0, size=400)
variant = rng.normal(loc=46.0, scale=12.0, size=400)

t_result = stats.ttest_ind(variant, control, equal_var=False)
note(
    f"Control mean: <strong>${control.mean():.2f}</strong>, "
    f"variant mean: <strong>${variant.mean():.2f}</strong>. "
    f"Welch's t = {t_result.statistic:.2f}, "
    f"p = {t_result.pvalue:.4f}."
)

# Fit a normal distribution to each group and overlay the PDFs.
x = np.linspace(0, 90, 300)
ctrl_mu, ctrl_sigma = stats.norm.fit(control)
var_mu, var_sigma = stats.norm.fit(variant)

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(control, bins=30, density=True, alpha=0.4,
        color="gray", label="Control")
ax.hist(variant, bins=30, density=True, alpha=0.4,
        color="seagreen", label="Variant")
ax.plot(x, stats.norm.pdf(x, ctrl_mu, ctrl_sigma),
        color="black", linewidth=2)
ax.plot(x, stats.norm.pdf(x, var_mu, var_sigma),
        color="darkgreen", linewidth=2)
ax.set_title("Order value distributions with fitted normals")
ax.set_xlabel("Order value ($)")
ax.set_ylabel("Density")
ax.legend()
fig.tight_layout()
display(fig, append=True)

# Use scipy.integrate.quad to compute the probability that a
# variant order exceeds $60, by integrating its fitted PDF.
prob_above_60, abs_error = integrate.quad(
    lambda v: stats.norm.pdf(v, var_mu, var_sigma),
    60, np.inf,
)
note(
    f"Integrating the fitted variant PDF from $60 to &infin; gives "
    f"P(order &gt; $60) &approx; <strong>{prob_above_60:.3f}</strong> "
    f"(quad error estimate: {abs_error:.1e})."
)

# Solve a small ODE with solve_ivp: logistic growth of signups.
def logistic(t, y, r=0.6, capacity=1000):
    """Population growth toward a carrying capacity."""
    return r * y * (1 - y / capacity)


solution = integrate.solve_ivp(
    logistic, t_span=(0, 20), y0=[10.0], dense_output=True,
)
t_grid = np.linspace(0, 20, 200)
y_grid = solution.sol(t_grid)[0]

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(t_grid, y_grid, color="purple", linewidth=2)
ax.axhline(1000, color="gray", linestyle="--", label="Carrying capacity")
ax.set_title("Logistic growth solved with scipy.integrate.solve_ivp")
ax.set_xlabel("Days")
ax.set_ylabel("Active users")
ax.legend()
fig.tight_layout()
display(fig, append=True)
