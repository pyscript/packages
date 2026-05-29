"""
A friendly tour of python-dateutil.

The standard library's `datetime` is great for representing instants,
but it's awkward when you need to *parse* messy human input or do
calendar-aware arithmetic like "the third Friday of next month."
That's where `dateutil` shines.

Docs: https://dateutil.readthedocs.io/en/stable/
"""
from IPython.core.display import display, HTML

# ---------------------------------------------------------------------
# Section 1: Parsing dates from almost any string format.
# ---------------------------------------------------------------------

heading("1. Parsing messy date strings")
note(
    "A small batch of timestamps written by different people, in "
    "different formats. dateutil.parser.parse handles them all."
)

raw_timestamps = [
    "2024-03-15T09:41:00",
    "March 15, 2024 9:41 AM",
    "15/03/2024 09:41",
    "Fri, 15 Mar 2024 09:41:00 +0100",
    "20240315T094100",
]

rows = []
for raw in raw_timestamps:
    parsed = parse(raw)
    rows.append(f"<tr><td><code>{raw}</code></td><td>{parsed}</td></tr>")

display(HTML(
    "<table border='1' cellpadding='6' cellspacing='0'>"
    "<tr><th>Input</th><th>Parsed datetime</th></tr>"
    + "".join(rows) +
    "</table>"
), append=True)

# Fuzzy parsing pulls a date out of surrounding prose.
sentence = "The package was shipped on Tuesday, April 12th 2022 at 5pm."
note(f"Fuzzy parse of: <em>{sentence}</em>")
note(f"Result: <strong>{parse(sentence, fuzzy=True)}</strong>")

# Day-first vs. month-first ambiguity.
note(
    "The string '04-05-2024' is ambiguous. dateutil lets you steer it: "
    f"default reads it as <strong>{parse('04-05-2024').date()}</strong>, "
    f"while dayfirst=True reads it as "
    f"<strong>{parse('04-05-2024', dayfirst=True).date()}</strong>."
)

# ---------------------------------------------------------------------
# Section 2: relativedelta for calendar-aware arithmetic.
# ---------------------------------------------------------------------

heading("2. relativedelta: calendar-aware date math")
note(
    "Unlike timedelta (which only knows about fixed durations), "
    "relativedelta understands months, years, and weekday targets."
)

today = date(2024, 3, 15)
note(f"Anchor date: <strong>{today}</strong> (a Friday).")

examples = [
    ("Three months from now",
        today + relativedelta(months=+3)),
    ("One year and two months ago",
        today + relativedelta(years=-1, months=-2)),
    ("Next Monday",
        today + relativedelta(weekday=MO(+1), days=+1)),
    ("Last Friday of this month",
        today + relativedelta(day=31, weekday=FR(-1))),
    ("First Sunday of next month",
        today + relativedelta(months=+1, day=1, weekday=SU(+1))),
    ("End-of-month rollover from Jan 31",
        date(2024, 1, 31) + relativedelta(months=+1)),
]

rows = [
    f"<tr><td>{label}</td><td><strong>{value}</strong></td></tr>"
    for label, value in examples
]
display(HTML(
    "<table border='1' cellpadding='6' cellspacing='0'>"
    "<tr><th>Question</th><th>Answer</th></tr>"
    + "".join(rows) +
    "</table>"
), append=True)

# The difference between two dates as a calendar-aware delta.
born = date(1995, 7, 22)
age = relativedelta(today, born)
note(
    f"Someone born on {born} is "
    f"<strong>{age.years} years, {age.months} months, "
    f"and {age.days} days</strong> old on {today}."
)
