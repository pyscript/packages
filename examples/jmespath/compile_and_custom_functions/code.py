# When you'll run the same query against many documents, compile it once
# and reuse the parsed expression. You can also extend the language with
# your own functions via jmespath.Options.
import jmespath
from jmespath import functions


# Imagine a stream of telemetry packets from weather stations.
packets = [
    {"station": "Alpha",   "readings": {"temp_c": 18.2, "wind_kph": 22.0}},
    {"station": "Bravo",   "readings": {"temp_c": 21.7, "wind_kph": 5.4}},
    {"station": "Charlie", "readings": {"temp_c": 14.9, "wind_kph": 31.6}},
    {"station": "Delta",   "readings": {"temp_c": 26.1, "wind_kph": 12.3}},
]

heading("Compile once, search many")
note(
    "<code>jmespath.compile</code> parses the expression up front so "
    "repeated searches skip the parsing step."
)

# Reshape each packet into a flat record.
flatten = jmespath.compile(
    "{name: station, t: readings.temp_c, w: readings.wind_kph}"
)

flat_records = [flatten.search(p) for p in packets]
display(flat_records, append=True)

heading("Adding a custom function")
note(
    "Subclass <code>jmespath.functions.Functions</code>, define methods "
    "named <code>_func_&lt;name&gt;</code>, and register your subclass "
    "via <code>Options(custom_functions=...)</code>."
)


class WeatherFunctions(functions.Functions):
    """Domain-specific helpers for our telemetry packets."""

    @functions.signature({"types": ["number"]})
    def _func_c_to_f(self, celsius):
        """Convert a Celsius value to Fahrenheit."""
        return celsius * 9 / 5 + 32

    @functions.signature(
        {"types": ["number"]}, {"types": ["number"]},
    )
    def _func_beaufort_ok(self, temp_c, wind_kph):
        """Comfortable conditions: mild temp and gentle wind."""
        return 15 <= temp_c <= 25 and wind_kph < 20


options = jmespath.Options(custom_functions=WeatherFunctions())

# Use the custom functions inside JMESPath expressions.
fahrenheit = jmespath.search(
    "[*].{name: station, temp_f: c_to_f(readings.temp_c)}",
    packets,
    options=options,
)
note("Each station's temperature in Fahrenheit:")
display(fahrenheit, append=True)

comfortable = jmespath.search(
    "[?beaufort_ok(readings.temp_c, readings.wind_kph)].station",
    packets,
    options=options,
)
note(f"Stations with comfortable conditions: <strong>{comfortable}</strong>")
