# ---------------------------------------------------------------------
# Interactivity: drag a brush on one chart to filter another.
# ---------------------------------------------------------------------

heading("Brushing and linking: athletes' training data")
note(
    "Two charts that share a selection: drag a rectangle in the "
    "scatter plot to highlight athletes; the bar chart updates to "
    "show only the selected group's distribution by sport."
)

n = 200
sports = rng.choice(["Running", "Cycling", "Swimming", "Rowing"], size=n)
# Heart rate and weekly training hours, with sport-specific tendencies.
hours_per_week = rng.uniform(2, 18, size=n).round(1)
resting_hr = (
    72 - 1.4 * hours_per_week + rng.normal(0, 4, size=n)
).round(1).clip(40, 90)

athletes = pd.DataFrame({
    "athlete_id": np.arange(n),
    "sport": sports,
    "hours_per_week": hours_per_week,
    "resting_hr": resting_hr,
})

# An interval selection that we can attach to a chart and reference
# from other charts to filter or recolor.
brush = alt.selection_interval()

scatter = (
    alt.Chart(athletes)
    .mark_circle(size=70)
    .encode(
        x=alt.X("hours_per_week:Q", title="Training hours per week"),
        y=alt.Y("resting_hr:Q", title="Resting heart rate (bpm)"),
        # `alt.when(...).then(...).otherwise(...)` recolors based on selection.
        color=alt.when(brush).then("sport:N").otherwise(alt.value("lightgray")),
        tooltip=["sport", "hours_per_week", "resting_hr"],
    )
    .add_params(brush)
    .properties(width=420, height=300, title="Drag to select athletes")
)

bars = (
    alt.Chart(athletes)
    .mark_bar()
    .encode(
        x=alt.X("count():Q", title="Selected athletes"),
        y=alt.Y("sport:N", title=None),
        color="sport:N",
    )
    .transform_filter(brush)  # The bar chart only sees brushed rows.
    .properties(width=420, height=120, title="Counts by sport")
)

# `&` stacks charts vertically; `|` would place them side by side.
linked = scatter & bars
show_chart(linked)

note(
    "Two ideas worth keeping: <code>add_params</code> attaches a "
    "selection to a chart, and <code>transform_filter</code> uses "
    "that selection elsewhere. The same pattern works for dropdowns, "
    "sliders, and click selections."
)
