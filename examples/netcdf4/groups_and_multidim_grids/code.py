# ---------------------------------------------------------------------
# Multi-dimensional data, hierarchical groups, and CF-style time axes.
# ---------------------------------------------------------------------
#
# Real-world climate files often contain a (time, lat, lon) grid plus
# coordinate variables, organized into groups (like folders inside the
# file). Here we build a tiny synthetic temperature grid and use
# `num2date` to turn the numeric time axis into real datetimes.

heading("A gridded temperature field with groups")

climate = Dataset("climate.nc", mode="w", diskless=True, persist=False,
                  format="NETCDF4")
climate.Conventions = "CF-1.8"

# Define the spatial and temporal axes at the root.
n_time, n_lat, n_lon = 12, 9, 18
climate.createDimension("time", n_time)
climate.createDimension("lat", n_lat)
climate.createDimension("lon", n_lon)

t = climate.createVariable("time", "f8", ("time",))
t.units = "days since 2026-01-01 00:00:00"
t.calendar = "standard"
t[:] = np.arange(n_time) * 30  # roughly monthly

lat = climate.createVariable("lat", "f4", ("lat",))
lat.units = "degrees_north"
lat[:] = np.linspace(-80, 80, n_lat)

lon = climate.createVariable("lon", "f4", ("lon",))
lon.units = "degrees_east"
lon[:] = np.linspace(-170, 170, n_lon)

# Groups behave like sub-datasets; great for keeping observations and
# model output side by side in one file.
observations = climate.createGroup("observations")
temp = observations.createVariable(
    "air_temperature", "f4", ("time", "lat", "lon"),
    compression="zlib", complevel=4, least_significant_digit=2,
)
temp.units = "degrees_C"
temp.long_name = "Near-surface air temperature"

# Build a field that's warmer near the equator and drifts over the year.
lat_grid = lat[:][None, :, None]
month_phase = np.arange(n_time)[:, None, None] * 2 * np.pi / 12
field = (
    25 * np.cos(np.deg2rad(lat_grid))
    - 5
    + 3 * np.sin(month_phase)
    + rng.normal(0, 0.5, size=(n_time, n_lat, n_lon))
)
temp[:] = field.astype("f4")

note("The file's structure, including the nested group:")
display(HTML(f"<pre>{climate}</pre>"), append=True)
display(HTML(f"<pre>{observations}</pre>"), append=True)

# Decode the numeric time axis into Python/cftime datetimes.
dates = num2date(t[:], units=t.units, calendar=t.calendar)
note(f"First three time steps decoded: {[str(d)[:10] for d in dates[:3]]}")

# Average across longitude to get a zonal-mean Hovmöller diagram.
zonal_mean = temp[:].mean(axis=2)  # shape (time, lat)

fig, ax = plt.subplots(figsize=(8, 4))
mesh = ax.pcolormesh(
    np.arange(n_time), lat[:], zonal_mean.T, cmap="RdBu_r", shading="auto",
)
ax.set_xlabel("Month index")
ax.set_ylabel("Latitude (°N)")
ax.set_title("Zonal-mean air temperature (°C)")
fig.colorbar(mesh, ax=ax, label="°C")
fig.tight_layout()
display(fig, append=True)

climate.close()
