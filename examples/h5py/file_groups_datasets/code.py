"""
A first look at h5py.

HDF5 is a self-describing binary format for large, structured numerical
data. h5py exposes it through two simple ideas:

    * Groups behave like Python dictionaries.
    * Datasets behave like NumPy arrays.

We'll create a file in memory, write a couple of datasets organised
into groups, then reopen the file and read the data back. See the
docs at https://docs.h5py.org for the full reference.
"""
import numpy as np
import h5py
from IPython.core.display import display, HTML

heading("1. Writing an HDF5 file")
note(
    "We'll record a week of weather observations from two stations "
    "into a single HDF5 file. Each station gets its own group, and "
    "each measurement gets its own dataset."
)

# An in-memory file -- nothing touches disk, but the API is identical
# to a file on disk. The "w" mode creates (or truncates) the file.
filename = "weather.h5"
with h5py.File(filename, "w", driver="core", backing_store=False) as f:
    for station in ("kew", "heathrow"):
        group = f.create_group(station)
        # 7 days x 24 hours of synthetic temperature readings.
        temps = 12 + 6 * np.sin(np.linspace(0, 14 * np.pi, 7 * 24))
        temps += rng.normal(0, 1.0, size=temps.size)
        group.create_dataset("temperature_c", data=temps.round(2))
        group.create_dataset(
            "rainfall_mm",
            data=rng.gamma(1.5, 1.0, size=7).round(2),
        )
    note(f"File created with top-level groups: {list(f.keys())}")

    heading("2. Reading data back", level=3)
    # Datasets support NumPy-style slicing. Reading [...] pulls the
    # whole array; [a:b] reads only what you ask for.
    kew_temps = f["kew/temperature_c"][...]
    note(
        f"kew/temperature_c shape: {f['kew/temperature_c'].shape}, "
        f"dtype: {f['kew/temperature_c'].dtype}"
    )
    note(f"First six hourly readings at Kew: {kew_temps[:6].tolist()}")

    heading("3. Walking the hierarchy", level=3)
    # visititems calls our function for every object in the tree.
    rows = []
    def collect(name, obj):
        kind = "Group" if isinstance(obj, h5py.Group) else "Dataset"
        shape = getattr(obj, "shape", "")
        rows.append(f"<tr><td>{kind}</td><td>{name}</td>"
                    f"<td>{shape}</td></tr>")
    f.visititems(collect)
    display(HTML(
        "<table><tr><th>Kind</th><th>Path</th><th>Shape</th></tr>"
        + "".join(rows) + "</table>"
    ), append=True)
