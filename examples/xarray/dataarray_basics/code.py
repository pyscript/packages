"""
A first look at xarray.

Xarray adds labels (dimension names and coordinates) to NumPy-like
arrays so you can index, align, and aggregate by name instead of by
position. We'll build a small DataArray of sea-surface temperatures
across a 2D grid, then explore label-based selection and reductions.

Docs: https://docs.xarray.dev
"""
from IPython.core.display import display, HTML

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)


heading("A labeled 2D array: sea-surface temperature")
note(
    "Imagine a small patch of ocean sampled across a grid of "
    "latitude and longitude. We'll wrap a NumPy array in an "
    "xarray DataArray so the axes have meaningful labels."
)

# Build coordinate arrays. xarray uses these to label each axis.
latitudes = np.linspace(-10, 10, 5)       # degrees north
longitudes = np.linspace(120, 150, 7)     # degrees east

# Synthetic temperatures: warmer near the equator, with some noise.
base = 28 - 0.05 * latitudes[:, None] ** 2
sst_values = base + 0.5 * rng.standard_normal((5, 7))

sst = xr.DataArray(
    sst_values,
    coords={"lat": latitudes, "lon": longitudes},
    dims=("lat", "lon"),
    name="sst",
    attrs={"units": "degC", "description": "Sea-surface temperature"},
)

note("The DataArray prints with dims, coords, and attrs:")
display(sst, append=True)

# Label-based selection: pick by coordinate value, not integer index.
heading("Label-based selection with .sel()", level=3)
note(
    "Select the row at <code>lat=0</code> (the equator) and the "
    "value nearest to <code>lon=135</code>:"
)
equator = sst.sel(lat=0)
display(equator, append=True)

nearest_point = sst.sel(lat=0, lon=135, method="nearest")
note(f"Nearest point to (0°, 135°E): {float(nearest_point):.2f} °C")

# Reductions by dimension name, not axis number.
heading("Reductions by dimension name", level=3)
mean_by_lat = sst.mean(dim="lon")
note("Zonal mean (averaged across longitude):")
display(mean_by_lat, append=True)

# Plotting comes for free, with axes labeled from coords.
fig, ax = plt.subplots(figsize=(7, 4))
sst.plot(ax=ax, cmap="magma")
ax.set_title("Sea-surface temperature (°C)")
fig.tight_layout()
display(fig, append=True)
