# ---------------------------------------------------------------------
# Multiple Axes in one Figure, plus a few common chart types.
# ---------------------------------------------------------------------
# `plt.subplots(rows, cols)` returns a Figure and a 2D array of Axes.
# Each Axes is an independent plotting area you can address by index.
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)

heading("A 2x2 dashboard of chart types")
note(
    "One month of imaginary sales data for a small bakery, shown "
    "four ways: a bar chart, a histogram, a stacked area plot, "
    "and a box plot of weekday vs. weekend takings."
)

products = ["Bread", "Croissant", "Cake", "Cookie", "Tart"]
units_sold = rng.integers(80, 320, size=len(products))

n_days = 30
days = np.arange(1, n_days + 1)
bread = 60 + rng.normal(0, 8, size=n_days).cumsum() * 0.2 + 10
cakes = 30 + rng.normal(0, 5, size=n_days).cumsum() * 0.15 + 5
cookies = 45 + rng.normal(0, 6, size=n_days).cumsum() * 0.1 + 8

daily_total = bread + cakes + cookies
weekday_mask = (np.arange(n_days) % 7) < 5
weekday = daily_total[weekday_mask]
weekend = daily_total[~weekday_mask]

fig, axes = plt.subplots(2, 2, figsize=(10, 7))

# Top-left: bar chart of total units per product.
ax = axes[0, 0]
ax.bar(products, units_sold, color="tab:orange", edgecolor="black")
ax.set_title("Units sold by product")
ax.set_ylabel("Units")
ax.tick_params(axis="x", rotation=20)

# Top-right: histogram of daily total sales.
ax = axes[0, 1]
ax.hist(daily_total, bins=10, color="tab:blue",
        edgecolor="white")
ax.set_title("Distribution of daily totals")
ax.set_xlabel("Items sold per day")
ax.set_ylabel("Number of days")

# Bottom-left: stacked area plot of the three product lines over time.
ax = axes[1, 0]
ax.stackplot(days, bread, cakes, cookies,
             labels=["Bread", "Cakes", "Cookies"],
             colors=["#d4a373", "#e9c46a", "#a8dadc"],
             alpha=0.85)
ax.set_title("Daily sales by product line")
ax.set_xlabel("Day of month")
ax.set_ylabel("Items sold")
ax.legend(loc="upper left", fontsize=8)

# Bottom-right: box plot comparing weekdays and weekends.
ax = axes[1, 1]
ax.boxplot([weekday, weekend], labels=["Weekday", "Weekend"],
           patch_artist=True,
           boxprops=dict(facecolor="lightgreen"))
ax.set_title("Daily takings: weekday vs. weekend")
ax.set_ylabel("Items sold per day")

fig.suptitle("Bakery sales dashboard", fontsize=14, y=1.0)
fig.tight_layout()
display(fig, append=True)


# ---------------------------------------------------------------------
# Style sheets restyle a whole figure with one line.
# ---------------------------------------------------------------------
heading("Restyling with a built-in style sheet")
note(
    "Wrap plotting code in <code>plt.style.context(...)</code> to "
    "apply a style without affecting later plots. Try swapping in "
    "<code>'ggplot'</code> or <code>'seaborn-v0_8-darkgrid'</code>."
)

with plt.style.context("seaborn-v0_8-whitegrid"):
    fig, ax = plt.subplots(figsize=(8, 4))
    for label, mu in [("Branch A", 100), ("Branch B", 115),
                      ("Branch C", 92)]:
        values = mu + rng.normal(0, 8, size=n_days).cumsum() * 0.4
        ax.plot(days, values, marker="o", markersize=3, label=label)
    ax.set_title("Cumulative drift in three branches")
    ax.set_xlabel("Day")
    ax.set_ylabel("Index")
    ax.legend()
    fig.tight_layout()
    display(fig, append=True)
