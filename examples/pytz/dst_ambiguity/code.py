# ---------------------------------------------------------------------
# Handling the awkward parts: ambiguous and non-existent local times.
# ---------------------------------------------------------------------

heading("When a local time happens twice (or never)")
note(
    "On the morning the US falls back from EDT to EST, every "
    "wall-clock minute between 01:00 and 02:00 occurs twice. "
    "Conversely, in spring, 02:30 simply does not exist."
)

eastern = pytz.timezone("US/Eastern")
fmt = "%Y-%m-%d %H:%M:%S %Z%z"

# 01:30 on the fall-back morning is ambiguous. The is_dst flag tells
# pytz which of the two occurrences you mean.
ambiguous = datetime(2002, 10, 27, 1, 30)
during_dst = eastern.localize(ambiguous, is_dst=True)
after_dst = eastern.localize(ambiguous, is_dst=False)
note(f"01:30 interpreted as still-DST: <code>{during_dst.strftime(fmt)}</code>")
note(f"01:30 interpreted as post-DST:  <code>{after_dst.strftime(fmt)}</code>")

# Pass is_dst=None to refuse to guess and raise instead.
try:
    eastern.localize(ambiguous, is_dst=None)
except pytz.AmbiguousTimeError as exc:
    note(f"AmbiguousTimeError raised for: <code>{exc}</code>")

# Spring forward: 02:30 on 7 April 2002 simply doesn't exist.
nonexistent = datetime(2002, 4, 7, 2, 30)
try:
    eastern.localize(nonexistent, is_dst=None)
except pytz.NonExistentTimeError as exc:
    note(f"NonExistentTimeError raised for: <code>{exc}</code>")

heading("normalize() fixes arithmetic across DST boundaries")
note(
    "Subtracting 10 minutes from a wall-clock time can leave you "
    "in the wrong offset. normalize() re-snaps the result to the "
    "correct zone for that instant."
)

# Start just after the fall-back transition.
loc_dt = eastern.localize(datetime(2002, 10, 27, 1, 0))
before = loc_dt - timedelta(minutes=10)
note(f"Naive subtract:        <code>{before.strftime(fmt)}</code>")
note(f"After normalize():     <code>{eastern.normalize(before).strftime(fmt)}</code>")
