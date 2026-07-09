# ---------------------------------------------------------------------
# Datasets bundle multiple DataArrays that share dimensions.
# We'll build a small weather Dataset and use groupby to summarize
# by month, much like pandas groupby but along a labeled dimension.
# ---------------------------------------------------------------------

heading("A Dataset: daily weather across three cities")
note(
    "A Dataset is a dict-like container of DataArrays that share "
    "dimensions and coordinates. Here, every variable is indexed "
    "by <code>time</code> and <code>city</code>."
)

cities = ["Lisbon", "Reykjavik", "Singapore"]
days = 365
times = np.array(
    np.datetime64("2025-01-01") + np.arange(days),
    dtype="datetime64[D]",
)

# City-specific seasonal temperature curves (Singapore barely varies).
day_of_year = np.arange(days)
seasonal = np.array([
    18 + 8 * np.sin((day_of_year - 110) * 2 * np.pi / 365),  # Lisbon
    5 + 9 * np.sin((day_of_year - 110) * 2 * np.pi / 365),   # Reykjavik
    27 + 1.5 * np.sin((day_of_year - 110) * 2 * np.pi / 365),# Singapore
])
temperature = seasonal + rng.normal(0, 1.5, size=seasonal.shape)
precipitation = rng.gamma(shape=1.2, scale=2.0, size=seasonal.shape)

weather = xr.Dataset(
    data_vars={
        "temperature": (("city", "time"), temperature,
                        {"units": "degC"}),
        "precipitation": (("city", "time"), precipitation,
                          {"units": "mm"}),
    },
    coords={"city": cities, "time": times},
    attrs={"description": "Synthetic daily weather for three cities"},
)

note("The Dataset shows all variables and their shared coords:")
display(weather, append=True)

# Pull out a single variable: it's a DataArray.
heading("Selecting a variable and a city", level=3)
lisbon_temp = weather["temperature"].sel(city="Lisbon")
note(f"Lisbon temperature series: {lisbon_temp.sizes['time']} days.")
display(lisbon_temp.head(7) if hasattr(lisbon_temp, "head")
        else lisbon_temp.isel(time=slice(0, 7)), append=True)

# GroupBy over a virtual datetime accessor: 'time.month'.
heading("GroupBy: monthly means per city", level=3)
note(
    "Xarray exposes datetime components as <code>time.month</code>, "
    "<code>time.season</code>, etc. Group by them just like pandas."
)
monthly = weather.groupby("time.month").mean()
display(monthly["temperature"].round(2), append=True)

# Plot each city's monthly mean temperature on one axes.
fig, ax = plt.subplots(figsize=(8, 4))
for city in cities:
    monthly["temperature"].sel(city=city).plot(
        ax=ax, label=city, marker="o",
    )
ax.set_title("Monthly mean temperature by city")
ax.set_xlabel("Month")
ax.set_ylabel("Temperature (°C)")
ax.legend()
fig.tight_layout()
display(fig, append=True)
