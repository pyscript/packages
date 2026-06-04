"""
A first look at matplotlib: lines, markers, and a scatter plot.

Matplotlib's pyplot interface is the workhorse for quick plots. The
typical pattern is:

    fig, ax = plt.subplots()   # create a Figure and Axes
    ax.plot(x, y)              # draw something
    display(fig, append=True)  # show it

See the Matplotlib gallery for many more ideas:
https://matplotlib.org/stable/gallery/index.html
"""
from IPython.core.display import display, HTML

import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)


# ---------------------------------------------------------------------
# A simple line plot: two trig functions sharing one Axes.
# ---------------------------------------------------------------------
heading("A line plot: sine and cosine")
note(
    "We build an x array with NumPy, plot two curves on the same "
    "Axes, label them, and let matplotlib draw a legend."
)

x = np.linspace(0, 4 * np.pi, 200)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, np.sin(x), label="sin(x)", color="steelblue", linewidth=2)
ax.plot(x, np.cos(x), label="cos(x)", color="crimson",
        linewidth=2, linestyle="--")
ax.set_title("Sine and cosine")
ax.set_xlabel("x (radians)")
ax.set_ylabel("value")
ax.axhline(0, color="gray", linewidth=0.5)
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3)
fig.tight_layout()
display(fig, append=True)


# ---------------------------------------------------------------------
# A scatter plot: marker size and color encode extra dimensions.
# ---------------------------------------------------------------------
heading("A scatter plot: four dimensions in one figure")
note(
    "Each point is one of 80 imaginary cafes. Position shows price "
    "vs. rating, marker size shows daily customers, and color "
    "shows the cafe's age in years."
)

n_cafes = 80
price = rng.uniform(2.5, 6.0, size=n_cafes)
rating = 3.0 + 0.4 * price + rng.normal(0, 0.6, size=n_cafes)
rating = np.clip(rating, 1, 5)
customers = rng.integers(40, 400, size=n_cafes)
age_years = rng.uniform(1, 30, size=n_cafes)

fig, ax = plt.subplots(figsize=(8, 5))
scatter = ax.scatter(
    price, rating,
    s=customers,            # marker area in points^2
    c=age_years,            # mapped through the colormap
    cmap="viridis",
    alpha=0.75,
    edgecolor="black",
    linewidth=0.5,
)
ax.set_title("Cafes: price vs. rating")
ax.set_xlabel("Average drink price ($)")
ax.set_ylabel("Customer rating (1-5)")
fig.colorbar(scatter, ax=ax, label="Cafe age (years)")
fig.tight_layout()
display(fig, append=True)
