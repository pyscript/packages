"""
A first look at cftime.

cftime handles time the way climate and weather data do: with calendars
that don't always match the everyday Gregorian calendar. NetCDF files
typically encode time as a number ("days since 1900-01-01") together
with a calendar name. cftime turns those numbers into datetime-like
objects you can do arithmetic on.

Docs: https://unidata.github.io/cftime/
"""
from IPython.core.display import display, HTML

import numpy as np
import cftime


heading("Creating cftime.datetime instances")
note(
    "A cftime.datetime is calendar-aware. The same calendar date can "
    "live in different calendars and behave differently."
)

# A standard (mixed Julian/Gregorian) date.
launch = cftime.datetime(1957, 10, 4, 19, 28, 34, calendar="standard")
note(f"Sputnik launch (standard calendar): <code>{launch!r}</code>")
note(f"Day of week: {launch.strftime('%A')}; day of year: {launch.dayofyr}")

heading("Calendars that don't exist on your wall")
note(
    "Climate models often use idealized calendars. Here's the same "
    "nominal date in three different calendars."
)

for cal in ["standard", "noleap", "360_day"]:
    d = cftime.datetime(2000, 2, 29, calendar=cal) \
        if cal != "noleap" else cftime.datetime(2000, 2, 28, calendar=cal)
    note(f"<code>{cal:>10}</code>: {d!r} (days in month: {d.daysinmonth})")

heading("Decoding a NetCDF-style time axis")
note(
    "num2date converts numeric offsets plus a units string into "
    "cftime.datetime objects. This is exactly how time arrays in "
    "climate data files are read."
)

units = "hours since 2024-01-01 00:00:00"
hours_offsets = np.array([0, 6, 12, 18, 24, 36, 48])
times = cftime.num2date(hours_offsets, units=units, calendar="standard")

for offset, t in zip(hours_offsets, times):
    note(f"+{offset:>3} h &rarr; {t.isoformat()}")

heading("Round-tripping back to numbers with date2num")
back_to_numbers = cftime.date2num(times, units=units, calendar="standard")
note(f"date2num round-trip: {back_to_numbers.tolist()}")
