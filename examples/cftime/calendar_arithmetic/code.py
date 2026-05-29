# Arithmetic, differences, and crossing calendars.

heading("Adding timedeltas to cftime.datetime")
note(
    "cftime.datetime supports the same +/- timedelta arithmetic as "
    "Python's datetime, but it respects the chosen calendar."
)

start = cftime.datetime(2025, 1, 1, calendar="noleap")
one_year_later = start + timedelta(days=365)
note(
    f"On the <code>noleap</code> calendar, 365 days after "
    f"{start.isoformat()} is {one_year_later.isoformat()} "
    f"(no leap day, so it lands exactly a year on)."
)

start_360 = cftime.datetime(2025, 1, 1, calendar="360_day")
one_year_later_360 = start_360 + timedelta(days=360)
note(
    f"On the <code>360_day</code> calendar (12 months of 30 days), "
    f"360 days after {start_360.isoformat()} is "
    f"{one_year_later_360.isoformat()}."
)

heading("Subtracting two dates yields a timedelta")
apollo_11 = cftime.datetime(1969, 7, 20, 20, 17, calendar="standard")
moon_landing_50 = cftime.datetime(2019, 7, 20, 20, 17, calendar="standard")
elapsed = moon_landing_50 - apollo_11
note(f"From Apollo 11 to its 50th anniversary: {elapsed.days:,} days.")

heading("Parsing strings with strptime")
note(
    "Use cftime.datetime.strptime to parse formatted strings into a "
    "specific calendar."
)

raw = "2024-02-29T12:00:00"
parsed = cftime.datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S", calendar="julian")
note(f"Parsed <code>{raw}</code> on the Julian calendar: {parsed!r}")

heading("Switching calendars with change_calendar")
note(
    "The same instant in time looks different on different calendars. "
    "change_calendar converts between them."
)

julian_date = cftime.datetime(1582, 10, 4, calendar="julian")
gregorian = julian_date.change_calendar("proleptic_gregorian")
note(
    f"{julian_date.isoformat()} (julian) is the same instant as "
    f"{gregorian.isoformat()} (proleptic_gregorian) -- the famous "
    f"10-day jump from the 1582 calendar reform."
)

heading("Building a monthly time axis")
note(
    "A common pattern: generate a sequence of monthly timestamps for "
    "a model run, then convert to numeric offsets for storage."
)

months = [cftime.datetime(2030, m, 1, calendar="noleap") for m in range(1, 13)]
units = "days since 2030-01-01 00:00:00"
offsets = cftime.date2num(np.array(months), units=units, calendar="noleap")

for m, off in zip(months, offsets):
    note(f"{m.strftime('%Y-%m-%d')} &rarr; {int(off):>3} days since start")

note(
    f"Notice the gap is always 30 days on noleap... wait, no -- "
    f"on <code>noleap</code> February has 28 days, so the offsets "
    f"vary. Total length of the year: {int(offsets[-1]) + 30} days."
)
