# ---------------------------------------------------------------------
# Section 3: Recurrence rules - schedules, holidays, and exceptions.
# ---------------------------------------------------------------------
# Package imports for the example.
from datetime import datetime
from dateutil.parser import parse
from dateutil.rrule import (
    rrule, rruleset, rrulestr,
    YEARLY, MONTHLY, WEEKLY, DAILY,
    MO, TU, WE, TH, FR, SA, SU,
)


heading("3. rrule: generate schedules from recurrence rules")
note(
    "rrule implements the iCalendar RECUR specification. You can "
    "describe a schedule declaratively and iterate over its "
    "occurrences, just like a calendar app does behind the scenes."
)

# A standing meeting: every other Tuesday and Thursday at 10:00,
# for the next eight occurrences.
standup = rrule(
    WEEKLY,
    interval=2,
    byweekday=(TU, TH),
    count=8,
    dtstart=datetime(2024, 4, 2, 10, 0),
)

note("Bi-weekly stand-up on Tuesdays and Thursdays:")
display(HTML(
    "<ul>"
    + "".join(f"<li>{when:%a %Y-%m-%d %H:%M}</li>" for when in standup)
    + "</ul>"
), append=True)

# Every Friday the 13th in the 21st century (first six).
unlucky = rrule(
    YEARLY,
    byweekday=FR,
    bymonthday=13,
    count=6,
    dtstart=datetime(2024, 1, 1),
)

note("The next six Friday the 13ths:")
display(HTML(
    "<ul>"
    + "".join(f"<li>{when:%A, %B %d, %Y}</li>" for when in unlucky)
    + "</ul>"
), append=True)

# US Presidential Election Day: first Tuesday after a Monday in
# November, every 4 years. The bymonthday=(2..8) clause forces the
# Tuesday to fall after the first Monday of the month.
elections = rrule(
    YEARLY,
    interval=4,
    bymonth=11,
    byweekday=TU,
    bymonthday=(2, 3, 4, 5, 6, 7, 8),
    count=4,
    dtstart=datetime(2024, 1, 1),
)

note("Upcoming US Presidential Election Days:")
display(HTML(
    "<ul>"
    + "".join(f"<li>{when:%A, %B %d, %Y}</li>" for when in elections)
    + "</ul>"
), append=True)

# ---------------------------------------------------------------------
# rruleset: combine rules and add or remove specific dates.
# ---------------------------------------------------------------------

heading("4. rruleset: combining rules with exceptions")
note(
    "Real-world calendars are rarely a single clean rule. rruleset "
    "lets you union multiple rules, add one-off dates with rdate, "
    "and exclude dates with exdate."
)

# Daily for two weeks, but skip weekends and one specific holiday.
schedule = rruleset()
schedule.rrule(rrule(
    DAILY,
    count=14,
    dtstart=datetime(2024, 7, 1, 9, 0),
))
# Exclude all Saturdays and Sundays in this range.
schedule.exrule(rrule(
    DAILY,
    byweekday=(SA, SU),
    dtstart=datetime(2024, 7, 1, 9, 0),
    until=datetime(2024, 7, 15, 9, 0),
))
# Exclude US Independence Day, which falls inside the window.
schedule.exdate(datetime(2024, 7, 4, 9, 0))

note("Working days in the first half of July 2024:")
display(HTML(
    "<ul>"
    + "".join(f"<li>{when:%a %Y-%m-%d}</li>" for when in schedule)
    + "</ul>"
), append=True)

# ---------------------------------------------------------------------
# rrulestr: parse an iCalendar RRULE string directly.
# ---------------------------------------------------------------------

heading("5. rrulestr: parse iCalendar RRULE strings")
note(
    "If you already have an RFC 5545 RRULE string (for example, from "
    "an .ics file), rrulestr parses it directly."
)

ical_rule = """
DTSTART:20240115T080000
RRULE:FREQ=MONTHLY;BYDAY=3MO;COUNT=6
"""
note("Parsing: <code>FREQ=MONTHLY;BYDAY=3MO;COUNT=6</code> "
     "(third Monday of the month, six times):")

occurrences = list(rrulestr(ical_rule))
display(HTML(
    "<ul>"
    + "".join(f"<li>{when:%A, %B %d, %Y at %H:%M}</li>"
              for when in occurrences)
    + "</ul>"
), append=True)
