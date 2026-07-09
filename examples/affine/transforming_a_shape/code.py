# ---------------------------------------------------------------------
# Visualizing how a composed transform reshapes a polygon.
# ---------------------------------------------------------------------

heading("Transforming a house-shaped polygon")
note(
    "We define a small polygon resembling a house, then build a "
    "composed transform that scales it, rotates it, and shifts it. "
    "Applying the transform is just a list comprehension over the "
    "vertices."
)

# Vertices of a simple house outline (closed polygon).
house = [
    (0.0, 0.0),
    (2.0, 0.0),
    (2.0, 1.5),
    (1.0, 2.5),
    (0.0, 1.5),
    (0.0, 0.0),
]

# Compose: scale up, rotate 25 degrees, then translate to (4, 1).
# Remember: the rightmost transform is applied first.
transform = (
    Affine.translation(4.0, 1.0)
    * Affine.rotation(25.0)
    * Affine.scale(1.5)
)

note("The composed transform:")
display(transform, append=True)

# Apply the transform to every vertex.
transformed = [transform * point for point in house]

note("First three transformed vertices:")
for original, new in list(zip(house, transformed))[:3]:
    nx, ny = new
    note(f"({original[0]}, {original[1]}) → ({nx:.3f}, {ny:.3f})")

# Plot the original and transformed polygons side by side.
fig, ax = plt.subplots(figsize=(7, 5))

orig_x, orig_y = zip(*house)
new_x, new_y = zip(*transformed)

ax.fill(orig_x, orig_y, alpha=0.3, color="steelblue", label="Original")
ax.plot(orig_x, orig_y, color="steelblue", linewidth=2)

ax.fill(new_x, new_y, alpha=0.3, color="darkorange", label="Transformed")
ax.plot(new_x, new_y, color="darkorange", linewidth=2)

ax.set_aspect("equal")
ax.grid(True, linestyle=":", alpha=0.6)
ax.set_title("Scale 1.5x, rotate 25°, translate to (4, 1)")
ax.legend(loc="upper left")
fig.tight_layout()
display(fig, append=True)
