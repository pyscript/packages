# ---------------------------------------------------------------------
# The wasm_backend: static, Agg-rendered figures.
# ---------------------------------------------------------------------

# This example demonstrates the OTHER backend that matplotlib-pyodide
# ships: wasm_backend, which rasterizes via Agg and shows the result
# as a static image. Selecting it must happen before pyplot import.
import matplotlib
matplotlib.use("module://matplotlib_pyodide.wasm_backend")

import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)


heading("Switching to the static wasm_backend")
note(
    "The <code>wasm_backend</code> renders matplotlib's familiar Agg "
    "output into an HTML canvas as a static image. Pick it when you "
    "want pixel-perfect parity with desktop matplotlib (hatching, "
    "complex text, every artist) and don't need interactivity."
)
note(f"Active matplotlib backend: <code>{matplotlib.get_backend()}</code>")

# A scatter plot of two synthetic clusters, the kind of thing you might
# show after a quick clustering experiment.
n = 200
cluster_a = rng.normal(loc=(-1.5, 0.5), scale=0.6, size=(n, 2))
cluster_b = rng.normal(loc=(1.2, -0.3), scale=0.8, size=(n, 2))

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(
    cluster_a[:, 0], cluster_a[:, 1],
    color="seagreen", alpha=0.6, edgecolor="white", label="group A",
)
ax.scatter(
    cluster_b[:, 0], cluster_b[:, 1],
    color="indianred", alpha=0.6, edgecolor="white", label="group B",
)

# Mark the centroids with hatched markers; hatching is one of the
# things the Agg-based wasm_backend renders faithfully.
for points, color in [(cluster_a, "seagreen"), (cluster_b, "indianred")]:
    cx, cy = points.mean(axis=0)
    ax.scatter(cx, cy, s=300, facecolor="white", edgecolor=color,
               linewidth=2, hatch="///", zorder=3)

ax.set_title("Two synthetic clusters (rendered via Agg in WASM)")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend(loc="best")
ax.grid(True, linestyle=":", alpha=0.5)
fig.tight_layout()
display(fig, append=True)
