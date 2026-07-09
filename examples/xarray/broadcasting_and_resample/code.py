# ---------------------------------------------------------------------
# Two of xarray's superpowers: arithmetic broadcasts by dimension
# name (not shape), and time series resample like pandas but along
# any datetime-indexed dimension.
# ---------------------------------------------------------------------

heading("Broadcasting by dimension name")
note(
    "When you combine two DataArrays, xarray aligns them by their "
    "dimension <em>names</em>. No reshaping, no <code>None</code> "
    "indexing tricks."
)

# Hourly readings of power draw at three sensors over five days.
hours = np.array(
    np.datetime64("2025-06-01T00") + np.arange(24 * 5),
    dtype="datetime64[h]",
)
sensors = ["kitchen", "office", "garage"]

# A daily diurnal pattern, plus per-sensor offsets and noise.
diurnal = 0.5 + 0.4 * np.sin((np.arange(24) - 6) * 2 * np.pi / 24)
diurnal_5d = np.tile(diurnal, 5)

power = xr.DataArray(
    diurnal_5d[None, :] + rng.normal(0, 0.05, size=(3, len(hours))),
    coords={"sensor": sensors, "time": hours},
    dims=("sensor", "time"),
    name="power_kw",
)

# Per-sensor calibration offsets, indexed only by 'sensor'.
calibration = xr.DataArray(
    [0.10, -0.05, 0.20],
    coords={"sensor": sensors},
    dims=("sensor",),
)

# Broadcasting: 'sensor' aligns; 'time' is added automatically.
calibrated = power + calibration
note("Calibrated power has both dims, broadcast by name:")
display(calibrated, append=True)

# Resample along the time dimension to daily means.
heading("Resampling a datetime dimension", level=3)
note(
    "<code>resample(time='1D')</code> reduces along time in fixed "
    "buckets. We'll get one value per sensor per day."
)
daily_mean = calibrated.resample(time="1D").mean()
display(daily_mean.round(3), append=True)

# Rolling window smoothing over the hourly series.
smoothed = calibrated.rolling(time=6, center=True).mean()

fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
for sensor in sensors:
    calibrated.sel(sensor=sensor).plot(
        ax=axes[0], label=sensor, alpha=0.5,
    )
    smoothed.sel(sensor=sensor).plot(
        ax=axes[1], label=sensor, linewidth=2,
    )
axes[0].set_title("Hourly calibrated power")
axes[0].set_ylabel("kW")
axes[0].legend()
axes[1].set_title("6-hour rolling mean")
axes[1].set_ylabel("kW")
axes[1].legend()
fig.autofmt_xdate()
fig.tight_layout()
display(fig, append=True)
