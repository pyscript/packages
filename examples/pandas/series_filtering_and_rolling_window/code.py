# ---------------------------------------------------------------------
# Section 2: Series, boolean filtering, rolling window.
# ---------------------------------------------------------------------

heading("2. Series, filtering, and a rolling average: daily step counts")
note(
    "Ninety days of simulated step counts. We filter for "
    "'active' days over 10,000 steps, then smooth the noisy "
    "daily series with a 7-day rolling mean."
)

n_days = 90
dates = pd.date_range("2026-01-01", periods=n_days, freq="D")

# Wander around 8,000 steps with weekly swings and Gaussian noise.
base = 8000 + 1500 * np.sin(np.arange(n_days) * 2 * np.pi / 7)
noise = rng.normal(0, 1200, size=n_days)
steps = pd.Series(
    (base + noise).clip(min=0).round().astype(int),
    index=dates,
    name="steps",
)

note(f"Series length: {len(steps)} days. First week:")
display(steps.head(7).to_frame(), append=True)

active_days = steps[steps > 10_000]
note(
    f"Days over 10,000 steps: <strong>{len(active_days)}</strong> "
    f"out of {len(steps)}. Mean on active days: "
    f"<strong>{active_days.mean():.0f}</strong> steps."
)

# 7-day rolling mean to reveal the underlying trend.
rolling = steps.rolling(window=7, min_periods=1).mean()

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(steps.index, steps.values, color="lightgray",
        label="Daily steps")
ax.plot(rolling.index, rolling.values, color="darkorange",
        linewidth=2, label="7-day rolling mean")
ax.axhline(10_000, color="green", linestyle="--",
           linewidth=1, label="10,000 step target")
ax.set_title("Daily step count with 7-day smoothing")
ax.set_ylabel("Steps")
ax.legend(loc="upper right")
fig.autofmt_xdate()
fig.tight_layout()
display(fig, append=True)
