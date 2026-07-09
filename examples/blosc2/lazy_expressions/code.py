# ---------------------------------------------------------------------
# Lazy expressions: compute on compressed NDArrays without
# decompressing everything up front.
# ---------------------------------------------------------------------

import numpy as np
import blosc2

rng = np.random.default_rng(0)

heading("Computing on compressed data with lazy expressions")
note(
    "Arithmetic on NDArray objects builds a LazyArray: a small graph "
    "describing the computation. Nothing is evaluated until you call "
    ".compute() (returns a new NDArray) or [:] (returns NumPy). "
    "The engine streams chunks through the graph in parallel."
)

# Two synthetic 3D fields: think of them as monthly readings on a
# 200x200 spatial grid for 36 months.
shape = (36, 200, 200)
temperature = blosc2.asarray(
    (15.0 + 8.0 * rng.standard_normal(shape)).astype(np.float32)
)
humidity = blosc2.asarray(
    (60.0 + 12.0 * rng.standard_normal(shape)).astype(np.float32)
)

note(
    f"Two NDArrays of shape <code>{shape}</code> "
    f"(<strong>{temperature.schunk.nbytes / 1e6:.1f} MB</strong> each "
    f"uncompressed)."
)

# Build a derived "discomfort index" lazily. No data is touched yet.
discomfort = temperature + 0.05 * (humidity - 40.0) ** 2
note(f"Lazy expression type: <code>{type(discomfort).__name__}</code>.")

# Materialize the result as a new compressed NDArray.
discomfort_nd = discomfort.compute()
note(
    f"Computed NDArray shape: <code>{discomfort_nd.shape}</code>, "
    f"compressed size: "
    f"<strong>{discomfort_nd.schunk.cbytes / 1e6:.2f} MB</strong>."
)

# Reductions also work lazily and via blosc2's top-level functions.
monthly_mean = blosc2.mean(discomfort_nd, axis=(1, 2))[:]
hottest_month = int(np.argmax(monthly_mean))

note(
    f"Mean discomfort across the grid for the first 6 months: "
    f"<code>{np.array2string(monthly_mean[:6], precision=2)}</code>"
)
note(
    f"Hottest month overall: "
    f"<strong>month {hottest_month}</strong> "
    f"(mean discomfort {monthly_mean[hottest_month]:.2f})."
)

# You can slice a LazyArray directly to get just the region you need,
# evaluating only the chunks that intersect the slice.
first_year_corner = (temperature[:12, :5, :5]
                     + humidity[:12, :5, :5]).mean()
note(
    "Mean of (temperature + humidity) over the first year's "
    f"5x5 corner: <strong>{float(first_year_corner):.2f}</strong>."
)
