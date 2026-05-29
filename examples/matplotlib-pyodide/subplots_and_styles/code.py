# ---------------------------------------------------------------------
# Multi-panel dashboards on the html5_canvas_backend.
# ---------------------------------------------------------------------

heading("A four-panel dashboard")
note(
    "Once a backend is selected, you write ordinary matplotlib. "
    "Here's a small dashboard summarizing a week of pretend sensor "
    "readings: line, histogram, bar, and box plots all on one figure."
)

# Seven days of hourly readings from three sensors.
hours = np.arange(24 * 7)
sensor_names = ["kitchen", "garage", "attic"]
baselines = np.array([21.0, 18.0, 24.5])
readings = (
    baselines[:, None]
    + 2.0 * np.sin((hours - 14) * 2 * np.pi / 24)[None, :]
    + rng.normal(0, 0.6, size=(3, hours.size))
)

fig, axes = plt.subplots(2, 2, figsize=(10, 6))
((ax_line, ax_hist), (ax_bar, ax_box)) = axes

# Top-left: time series for each sensor.
for name, series in zip(sensor_names, readings):
    ax_line.plot(hours, series, linewidth=1.2, label=name)
ax_line.set_title("Hourly temperature")
ax_line.set_xlabel("hour of week")
ax_line.set_ylabel("°C")
ax_line.legend(loc="upper right", fontsize=8)

# Top-right: distribution of all readings.
ax_hist.hist(readings.ravel(), bins=30, color="slateblue",
             edgecolor="white")
ax_hist.set_title("Distribution of all readings")
ax_hist.set_xlabel("°C")

# Bottom-left: mean per sensor.
means = readings.mean(axis=1)
colors = ["#4c72b0", "#dd8452", "#55a868"]
ax_bar.bar(sensor_names, means, color=colors)
ax_bar.set_title("Mean temperature per sensor")
ax_bar.set_ylabel("°C")

# Bottom-right: a box plot to compare spread.
ax_box.boxplot(readings.T, tick_labels=sensor_names, patch_artist=True,
               boxprops=dict(facecolor="#eaeaf2"))
ax_box.set_title("Spread per sensor")
ax_box.set_ylabel("°C")

fig.suptitle("Week-long readings, drawn through matplotlib-pyodide",
             fontsize=13)
fig.tight_layout()
display(fig, append=True)

note(
    "Both backends expose the full matplotlib API; the only difference "
    "is the canvas they paint on. Pick "
    "<code>html5_canvas_backend</code> for crisp interactive charts and "
    "<code>wasm_backend</code> when you want exact Agg fidelity."
)
