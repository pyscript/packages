"""
Core pandas with matplotlib use cases.

All of this code is running in your browser. See pyscript.net
for how we do this!

Each section builds a small synthetic dataset and displays both
tabular output and a matplotlib figure via PyScript's `display`
function (inspired by and interchangeable with IPython's
`display` capabilities).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pyscript import HTML, display


# Deterministic randomness so reloads show the same data. Feel free to
# change this seed or remove it to get different data on each reload!
rng = np.random.default_rng(42)

# Helper functions to emit HTML headings and notes, for visual separation
# of sections and to provide explanatory text. You can safely ignore
# these.

def heading(text, level=2):
    # Emit a simple HTML heading so sections are visually separated.
    display(HTML(f"<h{level}>{text}</h{level}>"), append=True)


def note(text):
    # Emit a short paragraph of explanatory prose.
    display(HTML(f"<p>{text}</p>"), append=True)


# ---------------------------------------------------------------------
# Section 1: DataFrame basics, describe, groupby, bar chart.
# ---------------------------------------------------------------------

heading("1. DataFrame basics: a bookshop's inventory")
note(
    "A made-up inventory of 200 books across five genres. "
    "We'll look at the first few rows, summary statistics, and "
    "revenue grouped by genre."
)

genres = ["Fiction", "Non-fiction", "Poetry", "Science", "History"]
n_books = 200

books = pd.DataFrame({
    "title": [f"Book {i:03d}" for i in range(n_books)],
    "genre": rng.choice(genres, size=n_books),
    "price": rng.uniform(5, 35, size=n_books).round(2),
    "copies_sold": rng.integers(1, 500, size=n_books),
})
books["revenue"] = (books["price"] * books["copies_sold"]).round(2)

note("First five rows:")
display(books.head(), append=True)

note("Summary statistics for the numeric columns:")
display(books.describe().round(2), append=True)

# Group by genre and aggregate several columns at once.
by_genre = books.groupby("genre").agg(
    titles=("title", "count"),
    avg_price=("price", "mean"),
    total_copies=("copies_sold", "sum"),
    total_revenue=("revenue", "sum"),
).round(2).sort_values("total_revenue", ascending=False)

note("Aggregates per genre, sorted by total revenue:")
display(by_genre, append=True)

# Bar chart of revenue by genre.
fig, ax = plt.subplots(figsize=(8, 4))
by_genre["total_revenue"].plot(kind="bar", ax=ax, color="steelblue")
ax.set_title("Total revenue by genre")
ax.set_ylabel("Revenue ($)")
ax.set_xlabel("Genre")
ax.tick_params(axis="x", rotation=0)
fig.tight_layout()
display(fig, append=True)


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


# ---------------------------------------------------------------------
# Section 3: Time series with a DatetimeIndex, resample, dual-axis.
# ---------------------------------------------------------------------

heading("3. Time series: hourly weather, resampled to daily means")
note(
    "One month of synthetic hourly temperature and humidity "
    "readings. We resample to daily means and plot both series "
    "on a twin-axis chart."
)

hours = pd.date_range("2026-03-01", periods=24 * 30, freq="h")
hour_of_day = hours.hour.to_numpy()
day_index = np.arange(len(hours)) / 24

# Diurnal temperature swing plus a slow warming trend.
temperature = (
    12
    + 6 * np.sin((hour_of_day - 9) * 2 * np.pi / 24)
    + 0.15 * day_index
    + rng.normal(0, 1.0, size=len(hours))
)

# Humidity is loosely anti-correlated with temperature.
humidity = (
    70
    - 10 * np.sin((hour_of_day - 9) * 2 * np.pi / 24)
    + rng.normal(0, 5, size=len(hours))
).clip(20, 100)

weather = pd.DataFrame(
    {"temperature_c": temperature, "humidity_pct": humidity},
    index=hours,
)

note("First few hourly readings:")
display(weather.head().round(2), append=True)

# Resample hourly data down to daily means.
daily = weather.resample("D").mean().round(2)
note(f"Resampled to {len(daily)} daily means. First week:")
display(daily.head(7), append=True)

# Plot both series on a shared x-axis with two y-axes.
fig, ax_temp = plt.subplots(figsize=(9, 4))
ax_temp.plot(daily.index, daily["temperature_c"],
             color="crimson", linewidth=2, label="Temperature")
ax_temp.set_ylabel("Temperature (°C)", color="crimson")
ax_temp.tick_params(axis="y", labelcolor="crimson")

ax_hum = ax_temp.twinx()
ax_hum.plot(daily.index, daily["humidity_pct"],
            color="steelblue", linewidth=2, label="Humidity")
ax_hum.set_ylabel("Humidity (%)", color="steelblue")
ax_hum.tick_params(axis="y", labelcolor="steelblue")

ax_temp.set_title("Daily mean temperature and humidity")
fig.autofmt_xdate()
fig.tight_layout()
display(fig, append=True)


heading("Done.")
note(
    "Three sections, three figures, "
    "one cheerful PyScript at your service. 🤗"
)