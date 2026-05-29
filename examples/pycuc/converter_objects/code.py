# ---------------------------------------------------------------------
# Reusable converter objects with create_cuc()
# ---------------------------------------------------------------------

heading("Carry a value around as a converter object")
note(
    "When the same quantity is expressed in many units, "
    "pycuc.create_cuc(value, unit) wraps it in a small object whose "
    ".convert(target) method returns the value in any compatible unit."
)

# A weather station logged a gust of 22 m/s. Let's express it in a few
# transport-friendly units without retyping the value each time.
wind_gust = pycuc.create_cuc(22, "m/s")

reports = {
    "km/h": wind_gust.convert("km/h"),
    "mph": wind_gust.convert("mph"),
    "knot": wind_gust.convert("knot"),
    "ft/s": wind_gust.convert("ft/s"),
}

note("A 22 m/s gust, in several velocity units:")
for unit, value in reports.items():
    note(f"&nbsp;&nbsp;<strong>{value:7.2f}</strong> {unit}")

heading("A small conversion table")
note(
    "Build a tidy table of energy values by looping over a list of "
    "target units. The same pattern works for any PyCUC category."
)

battery_energy = pycuc.create_cuc(1.5, "kWh")
energy_units = ["J", "kJ", "Wh", "kWh", "cal", "kcal", "BTU"]

rows = "".join(
    f"<tr><td>{unit}</td>"
    f"<td style='text-align:right'>{battery_energy.convert(unit):,.3f}</td></tr>"
    for unit in energy_units
)
table_html = (
    "<table border='1' cellpadding='6' style='border-collapse:collapse'>"
    "<tr><th>Unit</th><th>1.5 kWh as...</th></tr>"
    f"{rows}</table>"
)
display(HTML(table_html), append=True)
