"""
A first taste of iminuit: fit a noisy decay curve with a least-squares
cost function. Minuit will find the best parameters and estimate the
uncertainties on each one.

Docs: https://scikit-hep.org/iminuit/
"""
from IPython.core.display import display, HTML

heading("Fitting an exponential decay")
note(
    "We have noisy measurements of a signal that we believe decays "
    "exponentially: <code>y = A * exp(-k * t) + c</code>. We want to "
    "recover the amplitude, decay rate, and baseline."
)


# The model we believe describes the data. The first argument is the
# independent variable; the rest are the parameters Minuit will fit.
def decay_model(t, amplitude, rate, baseline):
    return amplitude * np.exp(-rate * t) + baseline


# Generate synthetic measurements with known "true" parameters.
true_amplitude, true_rate, true_baseline = 5.0, 0.7, 1.2
t_data = np.linspace(0, 6, 40)
y_error = np.full_like(t_data, 0.2)
y_data = (
    decay_model(t_data, true_amplitude, true_rate, true_baseline)
    + rng.normal(0, y_error)
)

# LeastSquares is a ready-made cost function: it knows how to compare
# the model to data given per-point uncertainties.
cost = LeastSquares(t_data, y_data, y_error, decay_model)

# Pass starting values for each parameter by name.
minuit = Minuit(cost, amplitude=1.0, rate=0.1, baseline=0.0)
minuit.migrad()   # run the MIGRAD minimizer
minuit.hesse()    # estimate parameter uncertainties

note("Fit results, with one-sigma uncertainties:")
for name, value, error in zip(
    minuit.parameters, minuit.values, minuit.errors,
):
    note(f"<code>{name} = {value:.3f} &plusmn; {error:.3f}</code>")

note(f"Reduced chi-squared: <code>{minuit.fval / (len(t_data) - 3):.2f}</code>")

# Plot data and fitted curve.
fig, ax = plt.subplots(figsize=(8, 4))
ax.errorbar(t_data, y_data, yerr=y_error, fmt="o",
            color="gray", label="Data", markersize=4)
t_smooth = np.linspace(t_data.min(), t_data.max(), 200)
ax.plot(t_smooth, decay_model(t_smooth, *minuit.values),
        color="crimson", linewidth=2, label="Best fit")
ax.set_xlabel("t")
ax.set_ylabel("y")
ax.set_title("Exponential decay fit with iminuit")
ax.legend()
fig.tight_layout()
display(fig, append=True)
