"""
A first taste of fastparquet: write a DataFrame to a Parquet file
in the in-memory virtual filesystem, then read it back.

Parquet is a columnar storage format that's compact, fast, and
preserves dtypes. fastparquet is a pure-Python(+Cython) implementation
that integrates closely with pandas.

Docs: https://fastparquet.readthedocs.io
"""
from IPython.core.display import display, HTML

# A small synthetic dataset: temperature readings from weather stations.
n_rows = 500
stations = ["Reykjavik", "Lisbon", "Cairo", "Singapore", "Wellington"]

readings = pd.DataFrame({
    "station": rng.choice(stations, size=n_rows),
    "timestamp": pd.date_range("2026-01-01", periods=n_rows, freq="h"),
    "temperature_c": rng.normal(15, 8, size=n_rows).round(2),
    "humidity_pct": rng.uniform(30, 95, size=n_rows).round(1),
})

heading("1. Original DataFrame")
note("Five hundred hourly readings from five weather stations.")
display(readings.head(), append=True)

# Write to a Parquet file. Pyodide gives us a writable in-memory
# filesystem, so we can use a regular path.
path = "/tmp/weather.parq"
write(path, readings, compression="SNAPPY")
note(f"Wrote {len(readings)} rows to <code>{path}</code> with Snappy compression.")

# Read it back. ParquetFile gives us metadata first, without loading
# the whole file into memory.
parquet_file = ParquetFile(path)

heading("2. Parquet file metadata")
note(
    f"Columns: <code>{parquet_file.columns}</code><br>"
    f"Rows: <strong>{parquet_file.count()}</strong><br>"
    f"Row groups: <strong>{len(parquet_file.row_groups)}</strong>"
)

heading("3. Round-tripped DataFrame")
roundtripped = parquet_file.to_pandas()
display(roundtripped.head(), append=True)
note(
    f"Dtypes preserved? "
    f"<strong>{(readings.dtypes == roundtripped.dtypes).all()}</strong>"
)
