# ---------------------------------------------------------------------
# Asymmetric errors via MINOS, plus a 1D likelihood profile plot.
# ---------------------------------------------------------------------

heading("Going beyond symmetric error bars")
note(
    "HESSE gives a symmetric Gaussian approximation to the parameter "
    "uncertainties. MINOS does better when the likelihood is skewed: "
    "it walks along the cost function until it climbs by a fixed amount, "
    "yielding asymmetric &plusmn; intervals."
)


# A small calibration dataset: signal counts vs. exposure time.
def power_model(t, normalization, exponent):
    return normalization * t ** exponent


t_data = np.linspace(0.5, 5.0, 12)
true_norm, true_exp = 3.0, 1.4
y_error = 0.5 + 0.1 * t_data
y_data = power_model(t_data, true_norm, true_exp) + rng.normal(0, y_error)

cost = LeastSquares(t_data, y_data, y_error, power_model)
minuit = Minuit(cost, normalization=1.0, exponent=1.0)
minuit.limits["normalization"] = (0, None)
minuit.migrad()
minuit.hesse()
minuit.minos()  # asymmetric intervals for all parameters

note("HESSE (symmetric) errors:")
display(minuit.errors.to_dict(), append=True)

note("MINOS (asymmetric) errors:")
for name in minuit.parameters:
    me = minuit.merrors[name]
    note(
        f"<code>{name}: {minuit.values[name]:.3f} "
        f"(+{me.upper:.3f} / {me.lower:.3f})</code>"
    )

# Visualize the 1D profile of the cost around the exponent parameter.
# `mnprofile` re-minimizes the other parameters at each point.
exponent_grid, fcn_values, _ = minuit.mnprofile("exponent", size=40)
fmin = minuit.fval

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(exponent_grid, fcn_values - fmin, color="purple", linewidth=2)
ax.axhline(1.0, color="gray", linestyle="--",
           label="Δχ² = 1 (1σ contour)")
ax.axvline(minuit.values["exponent"], color="black",
           linestyle=":", label="Best fit")
ax.set_xlabel("exponent")
ax.set_ylabel("χ² − χ²_min")
ax.set_title("Profile likelihood for the 'exponent' parameter")
ax.legend()
fig.tight_layout()
display(fig, append=True)
