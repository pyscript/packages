# ---------------------------------------------------------------------
# Munch + JSON: a comfortable way to work with API-shaped data.
# ---------------------------------------------------------------------
from munch import Munch, munchify, unmunchify
import json


heading("Parsing JSON into a Munch")
note(
    "Imagine this JSON came back from a weather API. We parse it as "
    "usual, then munchify so we can navigate the response with dots "
    "instead of a thicket of brackets and quotes."
)

api_response_text = """
{
    "location": {"city": "Reykjavik", "country": "IS"},
    "current": {"temperature_c": 4.2, "wind_kph": 22.0, "condition": "cloudy"},
    "forecast": [
        {"day": "Mon", "high_c": 5, "low_c": -1},
        {"day": "Tue", "high_c": 6, "low_c":  0},
        {"day": "Wed", "high_c": 3, "low_c": -2}
    ]
}
"""

raw = json.loads(api_response_text)
weather = munchify(raw)

note(f"weather.location.city &rarr; <strong>{weather.location.city}</strong>")
note(
    f"weather.current.temperature_c &rarr; "
    f"<strong>{weather.current.temperature_c} &deg;C</strong>"
)

# Iterate over a list of nested Munches just like a list of dicts.
forecast_lines = [
    f"{day.day}: {day.low_c}&deg; to {day.high_c}&deg;"
    for day in weather.forecast
]
note("Three-day forecast: " + " &middot; ".join(forecast_lines))

heading("Serializing back out with toJSON()")
note(
    "Every Munch has a toJSON() helper. It produces a JSON string just "
    "like json.dumps would, so a Munch can travel through any JSON-aware "
    "boundary unchanged."
)

# Mutate via dot access, then dump.
weather.current.condition = "snow"
weather.forecast.append(munchify({"day": "Thu", "high_c": 2, "low_c": -3}))

dumped = weather.toJSON()
note("Round-tripped JSON (truncated):")
display(HTML(f"<pre>{dumped[:200]}...</pre>"), append=True)

# And of course, it's still a dict, so json.dumps works directly too.
also_dumped = json.dumps(weather, indent=2)
note(f"json.dumps and toJSON agree: {json.loads(dumped) == json.loads(also_dumped)}")
