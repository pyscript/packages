# ---------------------------------------------------------------------
# Watching the clock jump: daylight saving transitions.
# ---------------------------------------------------------------------

heading("When does the clock spring forward and fall back?")
note(
    "tzdata knows the historical and scheduled DST rules for every "
    "IANA zone. Here we step minute-by-minute across the moments "
    "when New York and London change their offsets in 2025, and "
    "watch the local time skip or repeat."
)


def show_transition(zone_name, around_utc, label):
    """Print local time for each minute around a UTC instant."""
    zone = ZoneInfo(zone_name)
    rows = []
    for minutes_offset in range(-2, 3):
        moment_utc = around_utc + timedelta(minutes=minutes_offset)
        local = moment_utc.astimezone(zone)
        rows.append(
            f"<tr><td>{moment_utc:%Y-%m-%d %H:%M} UTC</td>"
            f"<td>{local:%Y-%m-%d %H:%M}</td>"
            f"<td>{local:%Z} (UTC{local:%z})</td></tr>"
        )
    table = (
        f"<h3>{label} &mdash; <code>{zone_name}</code></h3>"
        "<table><thead><tr><th>UTC</th><th>Local</th>"
        "<th>Abbrev / offset</th></tr></thead><tbody>"
        + "".join(rows) + "</tbody></table>"
    )
    display(HTML(table), append=True)


# Spring forward in the US: 2025-03-09 at 07:00 UTC (02:00 -> 03:00 local).
show_transition(
    "America/New_York",
    datetime(2025, 3, 9, 7, 0, tzinfo=ZoneInfo("UTC")),
    "Spring forward in New York",
)

# Fall back in the UK: 2025-10-26 at 01:00 UTC (02:00 -> 01:00 local).
show_transition(
    "Europe/London",
    datetime(2025, 10, 26, 1, 0, tzinfo=ZoneInfo("UTC")),
    "Fall back in London",
)

note(
    "Notice how the local minute jumps from 01:59 straight to 03:00 "
    "in New York (an hour vanishes), and how London replays the "
    "01:xx hour with a different abbreviation (BST then GMT)."
)
