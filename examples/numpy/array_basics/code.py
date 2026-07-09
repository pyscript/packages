"""
A first look at NumPy: arrays, vectorized math, and summary stats.

NumPy's core idea is the ndarray: a fixed-size, typed, N-dimensional
array that lets you express numeric computation as whole-array
expressions instead of Python loops.

Docs: https://numpy.org/doc/stable/
"""
import numpy as np
import matplotlib.pyplot as plt
from IPython.core.display import display, HTML


# A small story: hourly temperature readings from a weather station,
# in degrees Fahrenheit. We want to clean them up and summarize.
heading("From Python list to NumPy array")

readings_f = np.array(
    [58.2, 60.1, 63.7, 67.4, 71.0, 74.6, 76.2, 75.1, 71.9, 66.8],
    dtype=np.float64,
)

note(
    f"Shape: <code>{readings_f.shape}</code>, "
    f"dtype: <code>{readings_f.dtype}</code>, "
    f"size: <code>{readings_f.size}</code>"
)
display(readings_f, append=True)

# Vectorized arithmetic: convert F to C with a single expression that
# applies element-wise. No Python-level loop is involved.
heading("Vectorized math: Fahrenheit to Celsius")
readings_c = (readings_f - 32) * 5 / 9
display(readings_c.round(2), append=True)

# Summary methods live as both functions (np.mean) and methods (.mean()).
heading("Summary statistics")
note(
    f"min: <strong>{readings_c.min():.2f} &deg;C</strong> &middot; "
    f"max: <strong>{readings_c.max():.2f} &deg;C</strong> &middot; "
    f"mean: <strong>{readings_c.mean():.2f} &deg;C</strong> &middot; "
    f"std: <strong>{readings_c.std():.2f}</strong>"
)

# Boolean indexing: select array elements with a boolean mask.
heading("Boolean indexing")
warm = readings_c[readings_c > 20]
note(
    f"Hours above 20&deg;C: <strong>{warm.size}</strong>. "
    f"Their values:"
)
display(warm.round(2), append=True)

# A tiny plot to put it all together.
fig, ax = plt.subplots(figsize=(8, 3.5))
hours = np.arange(readings_c.size)
ax.plot(hours, readings_c, marker="o", color="crimson")
ax.axhline(readings_c.mean(), color="gray", linestyle="--",
           label=f"mean = {readings_c.mean():.1f} \u00b0C")
ax.set_xlabel("Hour")
ax.set_ylabel("Temperature (\u00b0C)")
ax.set_title("Hourly temperature")
ax.legend()
fig.tight_layout()
display(fig, append=True)
