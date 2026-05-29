# ---------------------------------------------------------------------
# The classic GIS use case: mapping raster pixels to world coordinates
# using a GDAL-style geotransform, then mapping back with the inverse.
# ---------------------------------------------------------------------

heading("Pixel ↔ world coordinates with from_gdal")
note(
    "Georeferenced rasters carry a 6-number GDAL geotransform: "
    "<code>(x_origin, x_pixel_size, x_skew, y_origin, y_skew, "
    "y_pixel_size)</code>. <code>Affine.from_gdal</code> turns that "
    "into an Affine you can use to translate between (column, row) "
    "pixel indices and (x, y) world coordinates."
)

# A made-up geotransform: 425-meter pixels, north-up, with origin
# in the upper-left (note the negative y pixel size).
geotransform = (-237481.5, 425.0, 0.0, 237536.4, 0.0, -425.0)
pixel_to_world = Affine.from_gdal(*geotransform)
world_to_pixel = ~pixel_to_world

note("Forward transform (pixel → world):")
display(pixel_to_world, append=True)

# A few points of interest on a 200x200 raster.
points_of_interest = {
    "upper-left corner": (0, 0),
    "center": (100, 100),
    "lower-right corner": (200, 200),
}

note("Pixel centers mapped to world coordinates:")
for label, (col, row) in points_of_interest.items():
    world_x, world_y = pixel_to_world * (col + 0.5, row + 0.5)
    note(
        f"<strong>{label}</strong> pixel ({col}, {row}) → "
        f"world ({world_x:.1f}, {world_y:.1f})"
    )

# Going the other way: which pixel contains a given world coordinate?
target_world = (-150_000.0, 100_000.0)
col_f, row_f = world_to_pixel * target_world
note(
    f"World point {target_world} falls in pixel "
    f"(col={int(col_f)}, row={int(row_f)})."
)

# Visualize the raster footprint and the points we computed.
fig, ax = plt.subplots(figsize=(7, 6))

# Outline of the full 200x200 raster in world coordinates.
corners_pixel = [(0, 0), (200, 0), (200, 200), (0, 200), (0, 0)]
corners_world = [pixel_to_world * c for c in corners_pixel]
fx, fy = zip(*corners_world)
ax.plot(fx, fy, color="black", linewidth=1.5, label="Raster footprint")
ax.fill(fx, fy, color="lightyellow", alpha=0.5)

# Plot the points of interest.
for label, (col, row) in points_of_interest.items():
    wx, wy = pixel_to_world * (col + 0.5, row + 0.5)
    ax.plot(wx, wy, "o", markersize=8)
    ax.annotate(label, (wx, wy), xytext=(8, 8),
                textcoords="offset points", fontsize=9)

# And the target world point.
ax.plot(*target_world, "x", color="red", markersize=12,
        markeredgewidth=2, label="Target world point")

ax.set_aspect("equal")
ax.set_xlabel("World X (m)")
ax.set_ylabel("World Y (m)")
ax.set_title("200×200 raster footprint in world coordinates")
ax.legend(loc="lower left")
ax.grid(True, linestyle=":", alpha=0.6)
fig.tight_layout()
display(fig, append=True)
