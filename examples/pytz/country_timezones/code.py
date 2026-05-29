# ---------------------------------------------------------------------
# Discovering timezones: country lookups and a small world clock.
# ---------------------------------------------------------------------

heading("Which timezones does a country use?")
note(
    "pytz exposes the IANA country tables. Look up zones by ISO 3166 "
    "two-letter country code, and pretty country names by the same key."
)

# country_timezones maps ISO codes to lists of zone names.
for code in ["nz", "us", "br", "ru"]:
    zones = pytz.country_timezones[code]
    name = pytz.country_names[code]
    note(f"<strong>{name}</strong> ({code.upper()}): {len(zones)} zones, "
         f"e.g. {', '.join(zones[:3])}{'...' if len(zones) > 3 else ''}")

heading("How big are the timezone lists?")
note(
    f"all_timezones contains <strong>{len(pytz.all_timezones)}</strong> "
    f"entries (everything in the IANA database, including historical "
    f"and deprecated names). common_timezones is a curated subset of "
    f"<strong>{len(pytz.common_timezones)}</strong> current zones."
)

heading("A small world clock")
note(
    "Render the same instant as wall-clock time in a handful of major "
    "cities. We render an HTML table for readability."
)

cities = [
    ("San Francisco", "America/Los_Angeles"),
    ("New York", "America/New_York"),
    ("London", "Europe/London"),
    ("Lagos", "Africa/Lagos"),
    ("Mumbai", "Asia/Kolkata"),
    ("Tokyo", "Asia/Tokyo"),
    ("Auckland", "Pacific/Auckland"),
]

# Pin a specific instant so the example is reproducible.
moment_utc = datetime(2024, 12, 21, 18, 0, 0, tzinfo=pytz.utc)

rows = ["<tr><th>City</th><th>Zone</th><th>Local time</th><th>Offset</th></tr>"]
for city, zone_name in cities:
    zone = pytz.timezone(zone_name)
    local = moment_utc.astimezone(zone)
    offset = local.strftime("%z")
    pretty_offset = f"{offset[:3]}:{offset[3:]}"
    rows.append(
        f"<tr><td>{city}</td><td><code>{zone_name}</code></td>"
        f"<td>{local.strftime('%Y-%m-%d %H:%M %Z')}</td>"
        f"<td>{pretty_offset}</td></tr>"
    )

table = (
    "<table style='border-collapse:collapse' border='1' cellpadding='6'>"
    + "".join(rows)
    + "</table>"
)
display(HTML(f"<p>Reference instant: <code>{moment_utc.isoformat()}</code></p>"),
        append=True)
display(HTML(table), append=True)
