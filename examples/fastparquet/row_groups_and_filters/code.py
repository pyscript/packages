# ---------------------------------------------------------------------
# Splitting a file into row groups and using filters to skip groups
# whose statistics rule them out. This is the foundation of fast
# analytical reads on large Parquet datasets.
# ---------------------------------------------------------------------

heading("Row groups: chunking a file for selective reads")
note(
    "A row group is a horizontal slice of the table. Each group "
    "stores per-column min/max statistics, so a reader can skip "
    "entire groups that can't possibly match a filter."
)

# Half a million sensor readings, sorted by timestamp so row groups
# correspond to contiguous time windows.
n_readings = 50_000
sensors = pd.DataFrame({
    "timestamp": pd.date_range("2026-01-01", periods=n_readings, freq="min"),
    "sensor_id": rng.integers(0, 20, size=n_readings),
    "value": rng.normal(100, 15, size=n_readings).round(3),
}).sort_values("timestamp").reset_index(drop=True)

# row_group_offsets carves the table into chunks at the given row
# indices. Here: ten groups of 5,000 rows each.
offsets = list(range(0, n_readings, 5_000))
write(
    "/tmp/sensors.parq",
    sensors,
    row_group_offsets=offsets,
    compression="SNAPPY",
)

parquet_file = ParquetFile("/tmp/sensors.parq")
note(
    f"File has <strong>{len(parquet_file.row_groups)}</strong> row groups, "
    f"<strong>{parquet_file.count()}</strong> rows total."
)

# Per-row-group time ranges from the file's statistics.
stats = parquet_file.statistics
group_ranges = pd.DataFrame({
    "min_timestamp": pd.to_datetime(stats["min"]["timestamp"]),
    "max_timestamp": pd.to_datetime(stats["max"]["timestamp"]),
    "min_value": stats["min"]["value"],
    "max_value": stats["max"]["value"],
})
note("First few row-group statistics:")
display(group_ranges.head().round(3), append=True)

# A filter is a list of (column, op, value) tuples. fastparquet uses
# row-group statistics to skip groups that can't match.
target_sensor = 7
filters = [
    ("sensor_id", "==", target_sensor),
    ("value", ">", 120.0),
]

filtered = parquet_file.to_pandas(filters=filters)
# Filters operate at row-group granularity, so apply them again
# row-wise for an exact result.
exact = filtered[
    (filtered["sensor_id"] == target_sensor)
    & (filtered["value"] > 120.0)
]

heading("Filtered result")
note(
    f"Rows where <code>sensor_id == {target_sensor}</code> and "
    f"<code>value &gt; 120</code>: <strong>{len(exact)}</strong>."
)
display(exact.head(), append=True)
