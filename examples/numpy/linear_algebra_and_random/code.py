# ---------------------------------------------------------------------
# Random sampling and a tiny linear regression by least squares.
# ---------------------------------------------------------------------

heading("Random sampling: simulating noisy measurements")
note(
    "We'll pretend we measured how much a spring stretches under "
    "different loads. The true relationship is linear, but our "
    "measurements are noisy."
)

# np.random.default_rng is the modern way to get a Generator. It
# exposes normal, uniform, integers, choice, and many more.
true_slope = 2.4      # cm of stretch per kg of load
true_intercept = 1.1  # cm at zero load

loads_kg = np.linspace(0, 10, 25)
noise = rng.normal(loc=0.0, scale=0.8, size=loads_kg.size)
stretch_cm = true_slope * loads_kg + true_intercept + noise

note(
    f"Mean noise: <code>{noise.mean():+.3f}</code>, "
    f"std: <code>{noise.std():.3f}</code>"
)

# ---------------------------------------------------------------------
# Solve for slope and intercept with np.linalg.lstsq.
# ---------------------------------------------------------------------

heading("Least-squares fit via np.linalg.lstsq")

# Build the design matrix [load, 1]; each row is one observation.
design = np.column_stack([loads_kg, np.ones_like(loads_kg)])
note(f"Design matrix shape: <code>{design.shape}</code>")

# lstsq returns (solution, residuals, rank, singular_values).
solution, *_ = np.linalg.lstsq(design, stretch_cm, rcond=None)
fit_slope, fit_intercept = solution

note(
    f"Recovered slope: <strong>{fit_slope:.3f}</strong> "
    f"(true {true_slope}) &middot; "
    f"intercept: <strong>{fit_intercept:.3f}</strong> "
    f"(true {true_intercept})"
)

# Coefficient of determination, R^2.
predictions = design @ solution
residuals = stretch_cm - predictions
ss_res = np.sum(residuals ** 2)
ss_tot = np.sum((stretch_cm - stretch_cm.mean()) ** 2)
r_squared = 1 - ss_res / ss_tot
note(f"R&sup2;: <strong>{r_squared:.4f}</strong>")

# ---------------------------------------------------------------------
# Plot the data, the true line, and the fitted line.
# ---------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(loads_kg, stretch_cm, color="steelblue",
           label="measurements", zorder=3)
ax.plot(loads_kg, true_slope * loads_kg + true_intercept,
        color="green", linestyle="--", label="true line")
ax.plot(loads_kg, predictions, color="crimson", linewidth=2,
        label=f"fit: y = {fit_slope:.2f}x + {fit_intercept:.2f}")
ax.set_xlabel("Load (kg)")
ax.set_ylabel("Stretch (cm)")
ax.set_title("Spring stretch vs. load")
ax.legend()
fig.tight_layout()
display(fig, append=True)
