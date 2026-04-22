# ---------------------------------------------------------------------
# Section 3: Time series with a DatetimeIndex, resample, dual-axis.
# ---------------------------------------------------------------------

heading("3. Time series: hourly weather, resampled to daily means")
note(
    "One month of synthetic hourly temperature and humidity "
    "readings. We resample to daily means and plot both series "
    "on a twin-axis chart."
)

hours = pd.date_range("2026-03-01", periods=24 * 30, freq="h")
hour_of_day = hours.hour.to_numpy()
day_index = np.arange(len(hours)) / 24

# Diurnal temperature swing plus a slow warming trend.
temperature = (
    12
    + 6 * np.sin((hour_of_day - 9) * 2 * np.pi / 24)
    + 0.15 * day_index
    + rng.normal(0, 1.0, size=len(hours))
)

# Humidity is loosely anti-correlated with temperature.
humidity = (
    70
    - 10 * np.sin((hour_of_day - 9) * 2 * np.pi / 24)
    + rng.normal(0, 5, size=len(hours))
).clip(20, 100)

weather = pd.DataFrame(
    {"temperature_c": temperature, "humidity_pct": humidity},
    index=hours,
)

note("First few hourly readings:")
display(weather.head().round(2), append=True)

# Resample hourly data down to daily means.
daily = weather.resample("D").mean().round(2)
note(f"Resampled to {len(daily)} daily means. First week:")
display(daily.head(7), append=True)

# Plot both series on a shared x-axis with two y-axes.
fig, ax_temp = plt.subplots(figsize=(9, 4))
ax_temp.plot(daily.index, daily["temperature_c"],
             color="crimson", linewidth=2, label="Temperature")
ax_temp.set_ylabel("Temperature (°C)", color="crimson")
ax_temp.tick_params(axis="y", labelcolor="crimson")

ax_hum = ax_temp.twinx()
ax_hum.plot(daily.index, daily["humidity_pct"],
            color="steelblue", linewidth=2, label="Humidity")
ax_hum.set_ylabel("Humidity (%)", color="steelblue")
ax_hum.tick_params(axis="y", labelcolor="steelblue")

ax_temp.set_title("Daily mean temperature and humidity")
fig.autofmt_xdate()
fig.tight_layout()
display(fig, append=True)
