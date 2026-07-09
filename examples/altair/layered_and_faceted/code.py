# ---------------------------------------------------------------------
# Layering marks together, and splitting one chart into many with facets.
# ---------------------------------------------------------------------

heading("Layering: city temperatures with a rolling mean")
note(
    "Sixty days of synthetic daily high temperatures for two cities. "
    "We layer a faint line of raw values under a thicker rolling mean "
    "to show both detail and trend in a single chart."
)

n_days = 60
dates = pd.date_range("2026-04-01", periods=n_days, freq="D")
cities = ["Lisbon", "Reykjavik"]
records = []
for city, base in zip(cities, [22, 8]):
    trend = base + 4 * np.sin(np.arange(n_days) * 2 * np.pi / 30)
    noise = rng.normal(0, 2.0, size=n_days)
    records.append(pd.DataFrame({
        "date": dates,
        "city": city,
        "temperature_c": (trend + noise).round(2),
    }))
weather = pd.concat(records, ignore_index=True)
weather["rolling_mean"] = (
    weather.groupby("city")["temperature_c"]
    .transform(lambda s: s.rolling(7, min_periods=1).mean())
)

base = alt.Chart(weather).encode(
    x=alt.X("date:T", title="Date"),
    color=alt.Color("city:N", title="City"),
)

# Two marks sharing the same data and x/color encodings, layered with `+`.
raw_line = base.mark_line(opacity=0.3).encode(y="temperature_c:Q")
smooth_line = base.mark_line(size=3).encode(
    y=alt.Y("rolling_mean:Q", title="Temperature (°C)")
)

layered = (raw_line + smooth_line).properties(
    title="Daily highs with 7-day rolling mean",
    width=520,
    height=260,
)
show_chart(layered)

heading("Faceting: one small chart per city")
note(
    "The <code>facet</code> operator splits the data by a column and "
    "draws a separate sub-chart for each value, sharing scales and "
    "axes. Great for comparing groups side by side."
)

faceted = (
    alt.Chart(weather)
    .mark_area(opacity=0.6)
    .encode(
        x=alt.X("date:T", title=None),
        y=alt.Y("temperature_c:Q", title="°C"),
        color="city:N",
    )
    .properties(width=240, height=160)
    .facet(column=alt.Column("city:N", title=None))
)
show_chart(faceted)
