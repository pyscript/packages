"""
A first look at pytz: attaching timezone information to a naive datetime
and converting between zones.

Note: Python 3.9+ ships zoneinfo in the standard library, which is now
the recommended choice for new code. pytz remains widely used for
backwards compatibility and is the focus of these examples.

Documentation: https://pythonhosted.org/pytz/
"""
from IPython.core.display import display, HTML

heading("Scheduling a launch across three time zones")
note(
    "A rocket launch is scheduled for 06:00 on 27 October 2002, "
    "local time at the launch site in New York. We use pytz to "
    "attach the correct timezone, then convert that exact instant "
    "to wall-clock times for teams in Amsterdam and Sydney."
)

# pytz exposes ready-made tzinfo objects via pytz.timezone(name).
# Names come from the IANA (Olson) database: "Region/City".
eastern = pytz.timezone("US/Eastern")
amsterdam = pytz.timezone("Europe/Amsterdam")
sydney = pytz.timezone("Australia/Sydney")

# IMPORTANT: with pytz, do NOT pass tzinfo= to datetime() for zones
# that have DST. Use the timezone's localize() method on a naive
# datetime instead. This picks the correct UTC offset for the date.
naive_launch = datetime(2002, 10, 27, 6, 0, 0)
launch_eastern = eastern.localize(naive_launch)

fmt = "%Y-%m-%d %H:%M:%S %Z%z"
note(f"Launch (New York): <code>{launch_eastern.strftime(fmt)}</code>")

# Once a datetime is timezone-aware, astimezone() converts the same
# instant in time into another zone's wall clock.
note(
    f"Same instant in Amsterdam: "
    f"<code>{launch_eastern.astimezone(amsterdam).strftime(fmt)}</code>"
)
note(
    f"Same instant in Sydney: "
    f"<code>{launch_eastern.astimezone(sydney).strftime(fmt)}</code>"
)

heading("UTC is the safe internal representation")
note(
    "The recommended pattern is to store and compute in UTC, then "
    "convert to a local zone only when displaying to a human."
)

# pytz.utc is a singleton; it's safe to pass directly as tzinfo.
now_utc = datetime(2024, 6, 15, 12, 0, 0, tzinfo=pytz.utc)
note(f"Reference instant (UTC): <code>{now_utc.strftime(fmt)}</code>")

for zone_name in ["US/Eastern", "Europe/London", "Asia/Tokyo"]:
    local = now_utc.astimezone(pytz.timezone(zone_name))
    note(f"{zone_name}: <code>{local.strftime(fmt)}</code>")
