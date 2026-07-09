# ---------------------------------------------------------------------
# Round-trip a netCDF dataset through a bytes buffer.
# ---------------------------------------------------------------------
#
# When a Dataset is opened with mode="w" and a `memory` size hint, calling
# .close() returns a memoryview holding the serialized file. Those bytes
# can be sent over the network, stored in a database, or re-opened as a
# read-only Dataset by passing them back via the `memory` kwarg.

import numpy as np
from netCDF4 import Dataset

rng = np.random.default_rng(0)


heading("Writing a netCDF file straight into a bytes buffer")

# Step 1: build a tiny weather station record in memory.
station = Dataset("station.nc", mode="w", memory=4096, format="NETCDF4")
station.station_id = "PSY-001"

station.createDimension("obs", 24)
hour = station.createVariable("hour", "i4", ("obs",))
hour.units = "hour of day"
hour[:] = np.arange(24)

humidity = station.createVariable("humidity", "f4", ("obs",))
humidity.units = "percent"
humidity[:] = (60 + 15 * np.sin(np.arange(24) * 2 * np.pi / 24)
               + rng.normal(0, 2, 24)).clip(0, 100).astype("f4")

# .close() with memory= returns a memoryview of the serialized dataset.
buffer = station.close()
raw_bytes = bytes(buffer)
note(f"Serialized dataset is {len(raw_bytes):,} bytes "
     f"(starts with magic {raw_bytes[:4]!r}).")

# Step 2: open those bytes again as a read-only Dataset.
reopened = Dataset("station.nc", mode="r", memory=raw_bytes)

heading("Inspecting the round-tripped dataset")
note("Global attributes survive the round trip:")
display(HTML(f"<pre>station_id = {reopened.station_id}</pre>"), append=True)

# Use ncattrs() and __dict__ to introspect attributes programmatically.
hum_var = reopened.variables["humidity"]
attrs = {name: hum_var.getncattr(name) for name in hum_var.ncattrs()}
display(HTML(
    f"<pre>humidity attributes: {attrs}\n"
    f"humidity dtype:      {hum_var.dtype}\n"
    f"humidity shape:      {hum_var.shape}\n"
    f"first 6 values:      {np.round(hum_var[:6], 2).tolist()}\n"
    f"daily mean:          {hum_var[:].mean():.2f}%</pre>"
), append=True)

# get_variables_by_attributes is a handy way to find variables by metadata.
percent_vars = reopened.get_variables_by_attributes(units="percent")
note(f"Variables measured in percent: {[v.name for v in percent_vars]}")

reopened.close()
