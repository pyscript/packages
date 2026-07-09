# ---------------------------------------------------------------------
# Moving windows: smoothing a noisy signal with bn.move_*
# ---------------------------------------------------------------------

import numpy as np
import bottleneck as bn
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)

heading("Smoothing noisy sensor data with moving windows")
note(
    "Bottleneck's <code>move_*</code> functions slide a fixed-size "
    "window along an array and compute a statistic at each step. "
    "They are the fast cousins of pandas' rolling operations."
)

# Two months of daily temperature readings (°C), with a slow seasonal
# trend, weekly wobble, and a healthy dose of measurement noise.
n_days = 60
day = np.arange(n_days)
truth = 10 + 0.1 * day + 2 * np.sin(day * 2 * np.pi / 14)
temperature = truth + rng.normal(0, 1.5, size=n_days)

# A 7-day moving mean smooths out the daily noise. `min_count=1` lets
# the result fill in at the very start instead of producing NaN.
smoothed = bn.move_mean(temperature, window=7, min_count=1)

# Moving min and max give you a running envelope -- handy for spotting
# when a signal breaks out of its recent range.
running_min = bn.move_min(temperature, window=7, min_count=1)
running_max = bn.move_max(temperature, window=7, min_count=1)

# Moving standard deviation tracks how volatile the signal has been.
running_std = bn.move_std(temperature, window=7, min_count=1)

note(
    f"Raw mean: <strong>{bn.nanmean(temperature):.2f} °C</strong>. "
    f"Mean of 7-day smoothing: "
    f"<strong>{bn.nanmean(smoothed):.2f} °C</strong>."
)

fig, (ax_signal, ax_vol) = plt.subplots(
    2, 1, figsize=(9, 6), sharex=True
)

ax_signal.fill_between(
    day, running_min, running_max,
    color="lightblue", alpha=0.6, label="7-day min/max envelope",
)
ax_signal.plot(day, temperature, "o", color="gray",
               markersize=3, label="Daily reading")
ax_signal.plot(day, smoothed, color="crimson", linewidth=2,
               label="7-day moving mean")
ax_signal.set_ylabel("Temperature (°C)")
ax_signal.set_title("Daily temperature with moving statistics")
ax_signal.legend(loc="upper left")

ax_vol.plot(day, running_std, color="darkorange", linewidth=2)
ax_vol.set_ylabel("7-day std (°C)")
ax_vol.set_xlabel("Day")
ax_vol.set_title("Rolling volatility")

fig.tight_layout()
display(fig, append=True)
