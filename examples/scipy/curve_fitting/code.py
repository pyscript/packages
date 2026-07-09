"""
A first taste of SciPy: fitting a model to noisy measurements.

SciPy (https://docs.scipy.org/doc/scipy/) is a huge collection of
scientific algorithms built on NumPy. We'll start with a classic
job: a lab tech recorded a cooling cup of coffee, and we want to
recover the underlying exponential decay from noisy temperature
readings.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from IPython.core.display import display, HTML

heading("Fitting Newton's law of cooling")
note(
    "We model temperature as T(t) = T_room + (T_0 - T_room) * exp(-k t). "
    "Given noisy data, scipy.optimize.curve_fit recovers the parameters."
)


def cooling(t, t_room, t_initial, k):
    """Newton's law of cooling: temperature vs. time."""
    return t_room + (t_initial - t_room) * np.exp(-k * t)


# True parameters and synthetic measurements.
true_params = dict(t_room=22.0, t_initial=92.0, k=0.18)
t_measured = np.linspace(0, 25, 30)
t_clean = cooling(t_measured, **true_params)
t_noisy = t_clean + rng.normal(0, 1.5, size=t_measured.size)

# curve_fit returns the best-fit parameters and a covariance matrix.
fitted, covariance = optimize.curve_fit(
    cooling, t_measured, t_noisy, p0=[20.0, 80.0, 0.1],
)
errors = np.sqrt(np.diag(covariance))

note("Recovered parameters (with 1-sigma uncertainties):")
labels = ["T_room (C)", "T_initial (C)", "k (1/min)"]
truths = [true_params["t_room"], true_params["t_initial"], true_params["k"]]
rows = "".join(
    f"<tr><td>{name}</td><td>{value:.3f} &plusmn; {err:.3f}</td>"
    f"<td>{truth:.3f}</td></tr>"
    for name, value, err, truth in zip(labels, fitted, errors, truths)
)
display(HTML(
    "<table border='1' cellpadding='4'>"
    "<tr><th>Parameter</th><th>Fitted</th><th>True</th></tr>"
    f"{rows}</table>"
), append=True)

# Plot data, true curve, and fit.
t_dense = np.linspace(0, 25, 200)
fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(t_measured, t_noisy, color="gray", label="Noisy readings")
ax.plot(t_dense, cooling(t_dense, **true_params),
        color="green", linestyle="--", label="True curve")
ax.plot(t_dense, cooling(t_dense, *fitted),
        color="crimson", linewidth=2, label="curve_fit result")
ax.set_xlabel("Time (minutes)")
ax.set_ylabel("Temperature (°C)")
ax.set_title("Cooling coffee: data and fitted model")
ax.legend()
fig.tight_layout()
display(fig, append=True)
