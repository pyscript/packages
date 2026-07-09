# ---------------------------------------------------------------------
# Filled contours: regions between adjacent z-levels.
# ---------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from contourpy import contour_generator

rng = np.random.default_rng(7)


heading("Filled contours: bands between levels")
note(
    "Use <code>filled(lower, upper)</code> for one band, or "
    "<code>multi_filled([z0, z1, z2, ...])</code> for several bands "
    "at once. Each band is returned as polygon points plus offsets "
    "marking where each polygon (and its holes) start and end."
)

# A field with a couple of peaks and a valley -- think temperature
# anomalies across a region.
grid_x, grid_y = np.meshgrid(
    np.linspace(-3, 3, 80),
    np.linspace(-3, 3, 80),
)
temperature_anomaly = (
    2.5 * np.exp(-((grid_x - 1) ** 2 + (grid_y - 1) ** 2) / 0.8)
    + 1.8 * np.exp(-((grid_x + 1.2) ** 2 + (grid_y - 0.5) ** 2) / 0.5)
    - 1.5 * np.exp(-((grid_x + 0.5) ** 2 + (grid_y + 1.5) ** 2) / 0.6)
)

# Use the "ChunkCombinedOffset" fill type so each band comes back as a
# (points, offsets) pair that's straightforward to turn into polygons.
cont_gen = contour_generator(
    x=grid_x, y=grid_y, z=temperature_anomaly,
    fill_type="ChunkCombinedOffset",
)

band_edges = [-1.5, -0.5, 0.5, 1.5, 2.5]
multi_filled = cont_gen.multi_filled(band_edges)

note(
    f"Computed <strong>{len(multi_filled)}</strong> filled bands "
    f"between {len(band_edges)} z-levels."
)

fig, ax = plt.subplots(figsize=(6, 5))
band_colours = plt.cm.RdBu_r(np.linspace(0.05, 0.95, len(multi_filled)))

# Each entry in multi_filled is a tuple of (points_list, offsets_list),
# one element per chunk. With unchunked output (the default), there's
# exactly one chunk.
for (points_list, offsets_list), colour in zip(multi_filled, band_colours):
    for chunk_points, chunk_offsets in zip(points_list, offsets_list):
        if chunk_points is None:
            continue
        # Walk the offsets to slice out each polygon's vertex ring.
        polygons = []
        for start, end in zip(chunk_offsets[:-1], chunk_offsets[1:]):
            polygons.append(Polygon(chunk_points[start:end], closed=True))
        ax.add_collection(
            PatchCollection(polygons, facecolor=colour, edgecolor="white",
                            linewidth=0.4)
        )

ax.set_xlim(grid_x.min(), grid_x.max())
ax.set_ylim(grid_y.min(), grid_y.max())
ax.set_aspect("equal")
ax.set_title("Filled contour bands of a temperature anomaly field")
ax.set_xlabel("x")
ax.set_ylabel("y")
fig.tight_layout()
display(fig, append=True)


# ---------------------------------------------------------------------
# Chunked grids: split the work into tiles.
# ---------------------------------------------------------------------

heading("Chunking a large grid")
note(
    "For larger grids you can split the domain into chunks. Each "
    "chunk's contours are computed independently, which keeps memory "
    "use predictable and is the foundation for multithreaded "
    "contouring. Here we colour the contour lines by chunk to show "
    "the tiling."
)

chunked_gen = contour_generator(
    x=grid_x, y=grid_y, z=temperature_anomaly,
    chunk_count=(4, 4),  # 4x4 = 16 chunks
    line_type="ChunkCombinedOffset",
)

# multi_lines with ChunkCombinedOffset returns, per level:
#   list over chunks of (points_list, offsets_list)
points_per_chunk, offsets_per_chunk = chunked_gen.lines(0.0)

fig, ax = plt.subplots(figsize=(6, 5))
ax.imshow(
    temperature_anomaly,
    extent=(grid_x.min(), grid_x.max(), grid_y.min(), grid_y.max()),
    origin="lower", cmap="RdBu_r", alpha=0.4,
)

chunk_colours = plt.cm.tab20(np.linspace(0, 1, len(points_per_chunk)))
for chunk_points, chunk_offsets, colour in zip(
    points_per_chunk, offsets_per_chunk, chunk_colours,
):
    if chunk_points is None:
        continue
    for start, end in zip(chunk_offsets[:-1], chunk_offsets[1:]):
        segment = chunk_points[start:end]
        ax.plot(segment[:, 0], segment[:, 1], color=colour, linewidth=1.5)

ax.set_title("Zero-level contour, coloured by chunk (4x4 tiling)")
ax.set_xlabel("x")
ax.set_ylabel("y")
fig.tight_layout()
display(fig, append=True)
