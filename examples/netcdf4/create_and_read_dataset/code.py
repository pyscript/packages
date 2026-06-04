"""
A first look at netCDF4: write a small dataset to memory, then read it back.

netCDF4 is the Python interface to the netCDF C library, the de-facto file
format for atmospheric, oceanographic, and climate data. A netCDF file is a
self-describing container of named dimensions, variables, and attributes.

Docs: https://unidata.github.io/netcdf4-python/
"""
from IPython.core.display import display, HTML

import numpy as np
from netCDF4 import Dataset

rng = np.random.default_rng(0)


# We use diskless=True so the file lives in browser memory rather than
# touching a real filesystem. With persist=False the bytes vanish on close.
ocean = Dataset("ocean_buoy.nc", mode="w", diskless=True, persist=False,
                format="NETCDF4")

# Global attributes describe the dataset as a whole.
ocean.title = "Synthetic ocean buoy readings"
ocean.institution = "PyScript Demo"
ocean.summary = "Hourly sea surface temperature for a single buoy."

# Dimensions are named axes. "time" is unlimited so we can append to it.
ocean.createDimension("time", None)

# Each dimension typically has a coordinate variable of the same name.
times = ocean.createVariable("time", "f8", ("time",))
times.units = "hours since 2026-01-01 00:00:00"
times.calendar = "gregorian"
times.long_name = "Time of observation"

# A data variable with a units attribute and an explicit fill value.
sst = ocean.createVariable("sst", "f4", ("time",), fill_value=-999.0)
sst.units = "degrees_C"
sst.long_name = "Sea surface temperature"

# Write 48 hours of data. Assigning to a slice grows an unlimited dimension.
n_hours = 48
hours = np.arange(n_hours, dtype="f8")
temperature = 14.5 + 0.8 * np.sin(hours * 2 * np.pi / 24) + rng.normal(0, 0.2, n_hours)

times[:] = hours
sst[:] = temperature.astype("f4")

heading("A netCDF dataset, summarized")
note("Printing the Dataset object gives a structured summary of its contents.")
display(HTML(f"<pre>{ocean}</pre>"), append=True)

heading("Reading variables back")
note(
    "netCDF variables behave like NumPy arrays. Slicing returns a NumPy "
    "(masked) array, and attributes like <code>units</code> are accessible "
    "as Python attributes."
)
display(HTML(
    f"<p><b>sst.units:</b> {sst.units}<br>"
    f"<b>sst.shape:</b> {sst.shape}<br>"
    f"<b>First 6 hours:</b> {np.round(sst[:6], 3).tolist()}<br>"
    f"<b>Mean SST:</b> {sst[:].mean():.3f} °C</p>"
), append=True)

ocean.close()
