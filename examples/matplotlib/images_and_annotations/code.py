# ---------------------------------------------------------------------
# 2D fields: imshow, contours, and pointing things out with annotations.
# ---------------------------------------------------------------------
# `imshow` displays a 2D array as a heatmap. `contour` draws iso-lines
# on the same Axes. `annotate` adds an arrow with a text label at any
# data coordinate. Together they're a great toolkit for explaining
# what's interesting about a field.

heading("Heatmap with contour lines and an annotated peak")
note(
    "We build a synthetic terrain by summing two 2D Gaussians, then "
    "render it as a heatmap, overlay contour lines, and point an "
    "arrow at the highest point."
)

# Build a grid of (x, y) coordinates spanning [-3, 3] in both axes.
grid = np.linspace(-3, 3, 200)
xx, yy = np.meshgrid(grid, grid)

# Two bumps of different heights to make the terrain interesting.
def gaussian(x, y, cx, cy, height, width):
    return height * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / width)

terrain = (
    gaussian(xx, yy, cx=-0.8, cy=-0.4, height=1.2, width=1.4)
    + gaussian(xx, yy, cx=1.1, cy=0.9, height=1.8, width=0.9)
)

# Locate the highest point in data coordinates for the annotation.
peak_index = np.unravel_index(np.argmax(terrain), terrain.shape)
peak_x = xx[peak_index]
peak_y = yy[peak_index]
peak_z = terrain[peak_index]

fig, ax = plt.subplots(figsize=(7, 6))
image = ax.imshow(
    terrain,
    extent=(grid.min(), grid.max(), grid.min(), grid.max()),
    origin="lower",
    cmap="terrain",
    aspect="equal",
)
contours = ax.contour(xx, yy, terrain, levels=8,
                      colors="black", linewidths=0.6, alpha=0.6)
ax.clabel(contours, inline=True, fontsize=8, fmt="%.1f")

ax.annotate(
    f"peak: {peak_z:.2f}",
    xy=(peak_x, peak_y),
    xytext=(peak_x - 1.8, peak_y + 1.4),
    fontsize=10,
    color="white",
    arrowprops=dict(arrowstyle="->", color="white", lw=1.5),
    bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.7),
)

ax.set_title("Synthetic terrain with contours")
ax.set_xlabel("x")
ax.set_ylabel("y")
fig.colorbar(image, ax=ax, label="elevation", shrink=0.85)
fig.tight_layout()
display(fig, append=True)


# ---------------------------------------------------------------------
# A polar projection shows that Axes are not always rectangular.
# ---------------------------------------------------------------------
heading("A polar plot of wind direction frequency")
note(
    "Matplotlib supports several projections. Pass "
    "<code>projection='polar'</code> to <code>subplots</code> and "
    "the Axes accepts angles (in radians) and radii."
)

# Twelve compass sectors, each with a synthetic count of wind readings.
n_sectors = 12
theta = np.linspace(0, 2 * np.pi, n_sectors, endpoint=False)
counts = 20 + 30 * np.abs(np.sin(theta - 0.7)) + rng.integers(0, 8, n_sectors)
width = 2 * np.pi / n_sectors

fig, ax = plt.subplots(figsize=(6, 6),
                       subplot_kw={"projection": "polar"})
bars = ax.bar(theta, counts, width=width, bottom=0,
              color=plt.cm.plasma(counts / counts.max()),
              edgecolor="white", linewidth=1)
ax.set_theta_zero_location("N")   # 0 degrees points up (north)
ax.set_theta_direction(-1)        # angles increase clockwise
ax.set_title("Wind direction frequency", pad=20)
fig.tight_layout()
display(fig, append=True)
