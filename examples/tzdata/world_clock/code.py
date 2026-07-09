"""
A first look at tzdata: providing IANA time zone data to Python's
zoneinfo module.

In a browser (or any system without a local zoneinfo database),
Python's standard `zoneinfo` module needs the tzdata package as a
fallback source of time zone data. Once tzdata is installed, you
can ask for any IANA time zone by name -- "Europe/Paris",
"Asia/Tokyo", "America/New_York" -- and zoneinfo finds the right
rules.
"""
from IPython.core.display import display, HTML

# Package imports for this example.
import tzdata
from datetime import datetime
from zoneinfo import ZoneInfo


heading("What version of the IANA database do we have?")
note(
    f"The tzdata package bundles a snapshot of the IANA time zone "
    f"database. This build provides version "
    f"<strong>{tzdata.IANA_VERSION}</strong>."
)

# Pick "now" once so every clock shows the same instant in different zones.
reference_moment = datetime.now(ZoneInfo("UTC"))

heading("The same instant in cities around the world")
note(
    "We take a single moment in UTC and translate it into local "
    "wall-clock time for a handful of IANA zones."
)

cities = [
    ("Auckland",       "Pacific/Auckland"),
    ("Tokyo",          "Asia/Tokyo"),
    ("Mumbai",         "Asia/Kolkata"),
    ("Paris",          "Europe/Paris"),
    ("London",         "Europe/London"),
    ("New York",       "America/New_York"),
    ("Los Angeles",    "America/Los_Angeles"),
    ("Honolulu",       "Pacific/Honolulu"),
]

rows = []
for city, zone_name in cities:
    local_time = reference_moment.astimezone(ZoneInfo(zone_name))
    rows.append(
        f"<tr><td>{city}</td><td><code>{zone_name}</code></td>"
        f"<td>{local_time:%Y-%m-%d %H:%M}</td>"
        f"<td>{local_time:%Z (UTC%z)}</td></tr>"
    )

table_html = (
    "<table><thead><tr><th>City</th><th>IANA key</th>"
    "<th>Local time</th><th>Offset</th></tr></thead>"
    "<tbody>" + "".join(rows) + "</tbody></table>"
)
display(HTML(table_html), append=True)
