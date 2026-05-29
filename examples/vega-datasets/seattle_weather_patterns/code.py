# ---------------------------------------------------------------------
# A small time-series story using the bundled seattle-weather dataset.
# ---------------------------------------------------------------------

heading("Four years of Seattle weather")
note(
    "<code>seattle_weather</code> ships with the package and contains "
    "daily weather observations: precipitation, temperatures, wind, "
    "and a categorical weather label. Note the underscore: dataset "
    "names with hyphens get converted to attribute-friendly names."
)

weather = data.seattle_weather()
weather["date"] = pd.to_datetime(weather["date"])
weather = weather.set_index("date").sort_index()
display(weather.head(), append=True)
note(
    f"Range: {weather.index.min().date()} to "
    f"{weather.index.max().date()} ({len(weather)} days)."
)

heading("How often does each kind of weather happen?")
counts = weather["weather"].value_counts()
display(counts.to_frame("days"), append=True)

fig, ax = plt.subplots(figsize=(7, 4))
counts.plot(kind="bar", ax=ax, color="slateblue")
ax.set_title("Days by weather type (2012-2015)")
ax.set_ylabel("Days")
ax.tick_params(axis="x", rotation=0)
fig.tight_layout()
display(fig, append=True)

heading("Monthly average temperature range")
# Resample to monthly means to smooth out daily noise.
monthly = weather[["temp_min", "temp_max"]].resample("MS").mean()

fig, ax = plt.subplots(figsize=(9, 4))
ax.fill_between(
    monthly.index, monthly["temp_min"], monthly["temp_max"],
    color="orange", alpha=0.3, label="Min-max range",
)
ax.plot(monthly.index, monthly["temp_max"],
        color="crimson", label="Monthly mean high")
ax.plot(monthly.index, monthly["temp_min"],
        color="steelblue", label="Monthly mean low")
ax.set_title("Seattle monthly temperature range")
ax.set_ylabel("Temperature (°C)")
ax.legend(loc="upper right")
fig.autofmt_xdate()
fig.tight_layout()
display(fig, append=True)

note(
    "From here, you could pull in any other Vega dataset by "
    "attribute access, for example <code>data.stocks()</code> or "
    "<code>data.gapminder()</code>. See "
    "<a href='https://github.com/altair-viz/vega_datasets'>the "
    "project page</a> for the full list."
)
