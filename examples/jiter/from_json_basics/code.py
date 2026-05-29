"""
A first look at jiter, a fast JSON parser from the Pydantic team.

The whole API is essentially one function: `jiter.from_json`. It takes
a `bytes` object (not a `str`) and returns native Python values, just
like the standard library's `json.loads`. See the project page for
details: https://github.com/pydantic/jiter
"""
from IPython.core.display import display, HTML

# jiter.from_json expects bytes -- note the leading `b`.
weather_report = b"""
{
    "station": "Kew Gardens",
    "recorded_at": "2026-04-12T09:00:00Z",
    "temperature_c": 14.2,
    "humidity_pct": 71,
    "observers": ["Ada", "Grace", "Lin"],
    "is_raining": false
}
"""

heading("1. Parse JSON bytes into a Python dict")
note(
    "jiter returns ordinary Python values: dicts, lists, strings, "
    "numbers, booleans, and None. Below, we parse a small weather "
    "report and pull values out by key."
)

report = jiter.from_json(weather_report)

display(report, append=True)
note(
    f"Station: <strong>{report['station']}</strong>. "
    f"Temperature: <strong>{report['temperature_c']} °C</strong>. "
    f"Observers: <strong>{', '.join(report['observers'])}</strong>."
)

heading("2. The string cache")
note(
    "By default, jiter caches parsed strings to speed up repeated "
    "keys and values. You can inspect and reset that cache."
)

# Parse a few records that share keys, so the cache gets a workout.
for _ in range(5):
    jiter.from_json(weather_report)

note(f"String cache size after parsing: <code>{jiter.cache_usage()}</code> bytes.")
jiter.cache_clear()
note(f"After <code>cache_clear()</code>: <code>{jiter.cache_usage()}</code> bytes.")
