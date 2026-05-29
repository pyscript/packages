"""
A first look at Vega-Altair: declarative statistical visualization.

Altair charts are built by combining three things:
  1. A data source (typically a pandas DataFrame).
  2. A mark (the visual primitive: point, bar, line, ...).
  3. Encodings that map data columns to visual channels (x, y, color, ...).

See https://altair-viz.github.io for the full documentation.
"""
from IPython.core.display import display, HTML

heading("A bakery's daily sales")
note(
    "Seven days of pastry sales at a small bakery. We'll plot the "
    "daily totals as a bar chart, mapping the day to the x-axis and "
    "the number of pastries sold to the y-axis."
)

bakery = pd.DataFrame({
    "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "pastries_sold": [42, 38, 55, 47, 73, 96, 81],
    "is_weekend": [False, False, False, False, False, True, True],
})

display(bakery, append=True)

# The classic Altair pattern: Chart(data) -> mark -> encode.
chart = (
    alt.Chart(bakery)
    .mark_bar()
    .encode(
        x=alt.X("day:N", sort=bakery["day"].tolist(), title="Day of week"),
        y=alt.Y("pastries_sold:Q", title="Pastries sold"),
        color=alt.Color("is_weekend:N", title="Weekend?"),
        tooltip=["day", "pastries_sold"],
    )
    .properties(title="Pastries sold per day", width=420, height=260)
)

show_chart(chart)

note(
    "The <code>:N</code> and <code>:Q</code> suffixes tell Altair the "
    "data type of each column: <em>nominal</em> (categories) and "
    "<em>quantitative</em> (numbers). Altair uses these to pick "
    "sensible scales and legends automatically."
)
